"""
Sistema de configuración centralizada para la aplicación.
"""

import os
import json
import yaml
import shutil
import logging
from typing import Dict, Any, Optional
from PyQt6.QtCore import QStandardPaths

# Configurar logger
logger = logging.getLogger("Config")


class Config:
    """
    Gestiona la configuración centralizada de la aplicación.
    Soporta formatos JSON y YAML.
    """

    _instance = None
    _config_data = None
    _config_path = None
    _config_dir = None

    @classmethod
    def get_instance(cls) -> 'Config':
        """
        Obtiene la instancia única de Config (patrón Singleton).

        Returns:
            Config: Instancia única de Config
        """
        if cls._instance is None:
            cls._instance = Config()
        return cls._instance

    def __init__(self):
        """Inicializa el sistema de configuración."""
        if Config._instance is not None:
            raise RuntimeError("Error: Usa Config.get_instance() para obtener la instancia.")

        self._init_config_paths()
        self._load_config()

    def _init_config_paths(self) -> None:
        """Inicializa las rutas de configuración."""
        # Determinar el directorio de configuración
        self._config_dir = os.path.join(
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation),
            "MinecraftBackupTool"
        )

        # Si no existe el directorio, buscamos alternativas
        if not os.path.exists(self._config_dir):
            # Crear el directorio
            try:
                os.makedirs(self._config_dir, exist_ok=True)
            except Exception as e:
                logger.warning(f"No se pudo crear el directorio de configuración: {e}")

                # Alternativa: usar directorio actual
                self._config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../config")
                os.makedirs(self._config_dir, exist_ok=True)

        # Ruta al archivo de configuración
        self._config_path = os.path.join(self._config_dir, "config.yaml")

    def _load_config(self) -> None:
        """Carga la configuración desde archivo o crea configuración predeterminada."""
        default_config = {
            "providers": {
                "java": True,
                "bedrock": True,
                "prism_launcher": False
            },
            "custom_paths": {
                "java": [],
                "bedrock": []
            },
            "appearance": {
                "theme": "dark",
                "language": "es",
                "show_splash": True,
                "show_tooltips": True
            },
            "backups": {
                "default_destination": "",
                "auto_backup_interval_days": 0,  # 0 = desactivado
                "compress_level": 6,  # 0-9 (0 = sin compresión, 9 = máxima compresión)
                "max_backups": 10,  # Número máximo de respaldos a mantener (0 = ilimitado)
                "include_screenshots": False
            },
            "updates": {
                "check_updates": True,
                "last_check": ""
            }
        }

        # Verificar si existe el archivo
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path, 'r', encoding='utf-8') as f:
                    if self._config_path.endswith('.json'):
                        self._config_data = json.load(f)
                    else:  # YAML por defecto
                        self._config_data = yaml.safe_load(f)

                # Aplicar valores predeterminados para claves no existentes
                self._ensure_defaults(self._config_data, default_config)
                logger.info(f"Configuración cargada desde {self._config_path}")
            except Exception as e:
                logger.error(f"Error al cargar configuración: {e}")

                # Crear respaldo del archivo corrupto
                backup_path = f"{self._config_path}.bak"
                try:
                    shutil.copy2(self._config_path, backup_path)
                    logger.info(f"Respaldo de configuración creado en {backup_path}")
                except Exception as backup_error:
                    logger.error(f"Error al crear respaldo de configuración: {backup_error}")

                # Usar valores predeterminados
                self._config_data = default_config
        else:
            # Usar valores predeterminados y guardar
            self._config_data = default_config
            self.save()
            logger.info("Configuración predeterminada creada")

    def _ensure_defaults(self, config: Dict[str, Any], defaults: Dict[str, Any]) -> None:
        """
        Asegura que todas las claves predeterminadas estén presentes en la configuración.

        Args:
            config: Configuración actual
            defaults: Valores predeterminados
        """
        for key, value in defaults.items():
            if key not in config:
                config[key] = value
            elif isinstance(value, dict) and isinstance(config[key], dict):
                self._ensure_defaults(config[key], value)

    def get(self, key: Optional[str] = None, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración.

        Args:
            key: Clave a obtener (puede ser anidada usando puntos, ej: "appearance.theme")
            default: Valor predeterminado si la clave no existe

        Returns:
            Any: Valor de configuración o valor predeterminado
        """
        if key is None:
            return self._config_data

        # Manejar claves anidadas (ej: "appearance.theme")
        keys = key.split('.')
        value = self._config_data

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Establece un valor de configuración.

        Args:
            key: Clave a establecer (puede ser anidada usando puntos)
            value: Valor a establecer
        """
        # Manejar claves anidadas (ej: "appearance.theme")
        keys = key.split('.')

        # Navegar hasta el último nivel
        config = self._config_data
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # Establecer el valor
        config[keys[-1]] = value

        # Guardar la configuración
        self.save()

    def save(self) -> bool:
        """
        Guarda la configuración en archivo.

        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(self._config_path), exist_ok=True)

            # Guardar en formato YAML
            with open(self._config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self._config_data, f, default_flow_style=False, allow_unicode=True)

            logger.info(f"Configuración guardada en {self._config_path}")
            return True
        except Exception as e:
            logger.error(f"Error al guardar configuración: {e}")
            return False

    def config_dir(self) -> str:
        """
        Obtiene la ruta al directorio de configuración.

        Returns:
            str: Ruta al directorio de configuración
        """
        return self._config_dir

    def reset(self) -> None:
        """Restablece la configuración a valores predeterminados."""
        # Renombrar el archivo actual si existe
        if os.path.exists(self._config_path):
            backup_path = f"{self._config_path}.old"
            try:
                shutil.move(self._config_path, backup_path)
                logger.info(f"Configuración actual respaldada en {backup_path}")
            except Exception as e:
                logger.error(f"Error al respaldar configuración actual: {e}")

        # Reinicializar la configuración
        self._load_config()
        logger.info("Configuración restablecida a valores predeterminados")


# Alias para facilitar el acceso
def get_config() -> Config:
    """
    Obtiene la instancia del sistema de configuración.

    Returns:
        Config: Instancia de configuración
    """
    return Config.get_instance()