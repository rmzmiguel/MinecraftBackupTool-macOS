"""
Sistema de registro (logging) mejorado para la aplicación.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
import traceback
from datetime import datetime
from typing import Optional, Dict, Any, Union

# Intentar importar el módulo de configuración
try:
    from app.utils.config import get_config

    has_config = True
except ImportError:
    has_config = False


class LogManager:
    """
    Gestiona el sistema de registro de la aplicación.
    Proporciona registros en consola y archivo con rotación.
    """

    _instance = None

    # Niveles de registro
    LEVELS = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    @classmethod
    def get_instance(cls) -> 'LogManager':
        """
        Obtiene la instancia única de LogManager (patrón Singleton).

        Returns:
            LogManager: Instancia única de LogManager
        """
        if cls._instance is None:
            cls._instance = LogManager()
        return cls._instance

    def __init__(self):
        """Inicializa el sistema de registro."""
        if LogManager._instance is not None:
            raise RuntimeError("Error: Usa LogManager.get_instance() para obtener la instancia.")

        self.initialized = False
        self.logger = None
        self.log_file = None

    def initialize(self, log_dir: Optional[str] = None, level: str = 'INFO') -> None:
        """
        Inicializa el sistema de registro.

        Args:
            log_dir: Directorio para almacenar los archivos de registro
            level: Nivel de registro ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
        """
        if self.initialized:
            return

        # Determinar directorio de logs
        if log_dir is None:
            if has_config:
                # Usar directorio de configuración
                config_dir = get_config().config_dir()
                log_dir = os.path.join(config_dir, 'logs')
            else:
                # Directorio en la raíz del proyecto
                log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../logs')

        # Crear directorio si no existe
        os.makedirs(log_dir, exist_ok=True)

        # Crear nombre de archivo con fecha
        timestamp = datetime.now().strftime('%Y%m%d')
        self.log_file = os.path.join(log_dir, f'minecraft_backup_tool_{timestamp}.log')

        # Convertir nivel a constante de logging
        log_level = self.LEVELS.get(level.upper(), logging.INFO)

        # Configurar logger raíz
        self.logger = logging.getLogger()
        self.logger.setLevel(log_level)

        # Eliminar handlers existentes
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Formato con timestamp, nivel y nombre del logger
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        self.logger.addHandler(console_handler)

        # Handler para archivo con rotación (máximo 5 archivos de 5MB cada uno)
        file_handler = RotatingFileHandler(
            self.log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        self.logger.addHandler(file_handler)

        # Registrar inicio
        self.logger.info(f"Inicialización del sistema de registro. Nivel: {level}")
        self.logger.info(f"Archivo de log: {self.log_file}")

        # Configurar captura de excepciones no manejadas
        self.setup_exception_handler()

        self.initialized = True

    def setup_exception_handler(self) -> None:
        """Configura el manejador de excepciones no capturadas."""

        def exception_handler(exc_type, exc_value, exc_traceback):
            """Manejador de excepciones no capturadas."""
            # Evitar duplicar excepciones KeyboardInterrupt/SystemExit
            if issubclass(exc_type, (KeyboardInterrupt, SystemExit)):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return

            # Registrar excepción con traceback completo
            self.logger.critical(
                f"Excepción no capturada: {exc_type.__name__}: {exc_value}",
                exc_info=(exc_type, exc_value, exc_traceback)
            )

        # Establecer manejador
        sys.excepthook = exception_handler

    def get_logger(self, name: str) -> logging.Logger:
        """
        Obtiene un logger con el nombre especificado.

        Args:
            name: Nombre del logger (generalmente el nombre del módulo)

        Returns:
            logging.Logger: Logger configurado
        """
        if not self.initialized:
            self.initialize()

        return logging.getLogger(name)

    def log_exception(self, e: Exception, logger_name: str = 'exception') -> None:
        """
        Registra una excepción con su traceback.

        Args:
            e: Excepción a registrar
            logger_name: Nombre del logger a utilizar
        """
        if not self.initialized:
            self.initialize()

        logger = logging.getLogger(logger_name)
        logger.error(f"Excepción: {type(e).__name__}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

    def get_log_file(self) -> Optional[str]:
        """
        Obtiene la ruta al archivo de registro actual.

        Returns:
            str: Ruta al archivo de registro o None si no está inicializado
        """
        return self.log_file if self.initialized else None


# Alias para facilitar el acceso
def setup_logging(log_dir: Optional[str] = None, level: str = 'INFO') -> None:
    """
    Configura el sistema de registro.

    Args:
        log_dir: Directorio para almacenar los archivos de registro
        level: Nivel de registro ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    """
    LogManager.get_instance().initialize(log_dir, level)


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger configurado.

    Args:
        name: Nombre del logger

    Returns:
        logging.Logger: Logger configurado
    """
    return LogManager.get_instance().get_logger(name)


def log_exception(e: Exception, logger_name: str = 'exception') -> None:
    """
    Registra una excepción con su traceback.

    Args:
        e: Excepción a registrar
        logger_name: Nombre del logger a utilizar
    """
    LogManager.get_instance().log_exception(e, logger_name)