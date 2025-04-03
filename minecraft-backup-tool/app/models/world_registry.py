"""
Registro central de proveedores de mundos de Minecraft.
Gestiona todos los proveedores y proporciona acceso unificado a todos los mundos.
"""

import os
import json
import yaml
import importlib.util
from typing import Dict, List, Any, Optional, Type

# Importación adelantada para anotaciones de tipo
from app.providers.base import WorldProvider


class WorldRegistry:
    """
    Registro centralizado para descubrir y gestionar mundos de Minecraft
    a través de múltiples proveedores.
    """
    
    _providers = []
    _config = None
    
    @classmethod
    def register_provider(cls, provider: WorldProvider) -> None:
        """
        Registra un nuevo proveedor de mundos.
        
        Args:
            provider: Instancia de un proveedor de mundos
        """
        cls._providers.append(provider)
    
    @classmethod
    def get_all_worlds(cls) -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtiene todos los mundos de todos los proveedores registrados.
        
        Returns:
            Dict[str, List[Dict]]: Diccionario donde la clave es el nombre de la plataforma
                                  y el valor es una lista de mundos
        """
        result = {}
        
        for provider in cls._providers:
            if provider.is_available():
                worlds = provider.get_worlds()
                if worlds:
                    result[provider.platform_name] = worlds
        
        return result
    
    @classmethod
    def initialize(cls, config_path: Optional[str] = None) -> None:
        """
        Inicializa el registro con la configuración y proveedores predeterminados.
        
        Args:
            config_path: Ruta opcional al archivo de configuración
        """
        # Cargar configuración
        cls._config = cls._load_config(config_path)
        
        # Importar aquí para evitar dependencias circulares
        from app.providers.java_provider import JavaWorldProvider
        from app.providers.bedrock_provider import BedrockWorldProvider
        
        # Registrar proveedores predeterminados si están habilitados en la configuración
        if cls._config.get('providers', {}).get('java', True):
            cls.register_provider(JavaWorldProvider())
            
        if cls._config.get('providers', {}).get('bedrock', True):
            cls.register_provider(BedrockWorldProvider())
        
        # Cargar proveedores adicionales
        try:
            if cls._config.get('providers', {}).get('prism_launcher', False):
                from app.providers.prism_provider import PrismLauncherProvider
                cls.register_provider(PrismLauncherProvider())
        except ImportError:
            # El proveedor de Prism es opcional
            pass
        
        # Cargar plugins personalizados si existen
        for plugin_path in cls._config.get('plugins', []):
            try:
                cls._load_plugin(plugin_path)
            except Exception as e:
                print(f"Error al cargar plugin {plugin_path}: {e}")
    
    @classmethod
    def _load_config(cls, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Carga la configuración desde un archivo o usa valores predeterminados.
        
        Args:
            config_path: Ruta al archivo de configuración
            
        Returns:
            Dict: Configuración cargada
        """
        default_config = {
            'providers': {
                'java': True,
                'bedrock': True,
                'prism_launcher': False
            },
            'custom_paths': {
                'java': [],
                'bedrock': [],
                'prism': []
            },
            'plugins': []
        }
        
        # Si no se especifica ruta, buscar en ubicaciones estándar
        if not config_path:
            possible_paths = [
                os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../config.yaml'),
                os.path.expanduser('~/.config/minecraft-backup-tool/config.yaml'),
                os.path.join(os.getcwd(), 'config.yaml')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        # Cargar desde archivo si existe
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.endswith('.json'):
                        config = json.load(f)
                    else:  # YAML por defecto
                        config = yaml.safe_load(f)
                
                # Combinar con valores por defecto
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                    elif isinstance(value, dict):
                        for subkey, subvalue in value.items():
                            if subkey not in config[key]:
                                config[key][subkey] = subvalue
                
                return config
            except Exception as e:
                print(f"Error al cargar configuración: {e}")
        
        # Usar valores por defecto si no hay configuración
        return default_config
    
    @classmethod
    def _load_plugin(cls, plugin_path: str) -> None:
        """
        Carga un plugin de proveedor de mundos externo.
        
        Args:
            plugin_path: Ruta al archivo del plugin
        """
        if not os.path.exists(plugin_path):
            raise FileNotFoundError(f"Plugin no encontrado: {plugin_path}")
            
        # Cargar módulo dinámicamente
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        plugin = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin)
        
        # El plugin debe tener una función register_providers
        if hasattr(plugin, 'register_providers'):
            plugin.register_providers(cls)
        else:
            raise AttributeError(f"El plugin {plugin_path} no tiene función register_providers")
    
    @classmethod
    def get_config(cls) -> Dict[str, Any]:
        """
        Obtiene la configuración actual.
        
        Returns:
            Dict: Configuración actual
        """
        if cls._config is None:
            cls._config = cls._load_config(None)
        return cls._config
