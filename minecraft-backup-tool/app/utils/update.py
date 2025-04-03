"""
Sistema para verificar actualizaciones de la aplicación.
"""

import os
import json
import logging
import tempfile
import webbrowser
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, Callable
from urllib.request import Request, urlopen
from urllib.error import URLError
from PyQt6.QtCore import QThread, pyqtSignal, QUrl

# Importar configuración
try:
    from app.utils.config import get_config
except ImportError:
    # Fallback para pruebas
    def get_config():
        class MockConfig:
            def get(self, key, default=None):
                return {"check_updates": True}

            def set(self, key, value):
                pass

        return MockConfig()

# Configuración de la versión actual
APP_VERSION = "1.0.0"
APP_NAME = "Minecraft Backup Tool"
GITHUB_REPO = "usuario/minecraft-backup-tool"  # Reemplazar con el repo real
UPDATE_CHECK_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

# Configurar logger
logger = logging.getLogger("UpdateSystem")


class UpdateChecker(QThread):
    """
    Hilo para verificar actualizaciones disponibles sin bloquear la UI.
    """

    # Señales para comunicar resultados
    update_available = pyqtSignal(str, str)  # versión nueva, URL
    no_updates = pyqtSignal()
    check_failed = pyqtSignal(str)  # mensaje de error

    def __init__(self, force_check: bool = False):
        """
        Inicializa el verificador de actualizaciones.

        Args:
            force_check: Si es True, ignora el intervalo mínimo entre verificaciones
        """
        super().__init__()
        self.force_check = force_check

    def run(self):
        """Ejecuta la verificación de actualizaciones en segundo plano."""
        try:
            # Verificar si se debe comprobar actualizaciones
            if not self._should_check_updates() and not self.force_check:
                self.no_updates.emit()
                return

            # Actualizar fecha de última verificación
            config = get_config()
            config.set('updates.last_check', datetime.now().isoformat())

            # Hacer la solicitud HTTP
            headers = {
                'User-Agent': f'{APP_NAME}/{APP_VERSION}',
                'Accept': 'application/vnd.github.v3+json'
            }
            req = Request(UPDATE_CHECK_URL, headers=headers)

            with urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    latest_version = data.get('tag_name', '').lstrip('v')
                    download_url = data.get('html_url', '')

                    # Comprobar si hay una nueva versión
                    if self._is_newer_version(latest_version):
                        self.update_available.emit(latest_version, download_url)
                    else:
                        self.no_updates.emit()
                else:
                    self.check_failed.emit(f"Error en la respuesta: {response.getcode()}")

        except URLError as e:
            logger.error(f"Error de conexión: {e}")
            self.check_failed.emit(f"Error de conexión: {str(e)}")
        except Exception as e:
            logger.error(f"Error al verificar actualizaciones: {e}")
            self.check_failed.emit(f"Error al verificar actualizaciones: {str(e)}")

    def _should_check_updates(self) -> bool:
        """
        Determina si se debe verificar actualizaciones según la configuración.

        Returns:
            bool: True si se debe verificar, False en caso contrario
        """
        config = get_config()

        # Verificar si está habilitada la comprobación de actualizaciones
        if not config.get('updates.check_updates', True):
            return False

        # Verificar la fecha de última comprobación (máximo una vez al día)
        last_check_str = config.get('updates.last_check', '')
        if last_check_str:
            try:
                last_check = datetime.fromisoformat(last_check_str)
                # Comprobar si ha pasado al menos un día desde la última verificación
                if datetime.now() - last_check < timedelta(days=1):
                    return False
            except (ValueError, TypeError):
                # Si hay error en el formato, hacer la verificación
                pass

        return True

    def _is_newer_version(self, latest_version: str) -> bool:
        """
        Compara la versión actual con la última versión disponible.

        Args:
            latest_version: Versión más reciente disponible

        Returns:
            bool: True si latest_version es más reciente, False en caso contrario
        """
        # Dividir versiones en componentes (major.minor.patch)
        try:
            current_parts = [int(x) for x in APP_VERSION.split('.')]
            latest_parts = [int(x) for x in latest_version.split('.')]

            # Asegurar que ambas listas tengan la misma longitud
            while len(current_parts) < 3:
                current_parts.append(0)
            while len(latest_parts) < 3:
                latest_parts.append(0)

            # Comparar componentes
            for i in range(3):
                if latest_parts[i] > current_parts[i]:
                    return True
                elif latest_parts[i] < current_parts[i]:
                    return False

            return False  # Versiones iguales
        except (ValueError, IndexError):
            # Si hay error en el formato, asumir que no hay actualización
            logger.warning(f"Error al comparar versiones: {APP_VERSION} vs {latest_version}")
            return False


class UpdateManager:
    """
    Gestiona la verificación y notificación de actualizaciones.
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> 'UpdateManager':
        """
        Obtiene la instancia única de UpdateManager (patrón Singleton).

        Returns:
            UpdateManager: Instancia única de UpdateManager
        """
        if cls._instance is None:
            cls._instance = UpdateManager()
        return cls._instance

    def __init__(self):
        """Inicializa el gestor de actualizaciones."""
        if UpdateManager._instance is not None:
            raise RuntimeError("Error: Usa UpdateManager.get_instance() para obtener la instancia.")

        self.update_checker = None
        self.notification_callback = None

    def check_for_updates(self, force_check: bool = False,
                          notification_callback: Optional[Callable[[str, str, str], None]] = None) -> None:
        """
        Inicia la verificación de actualizaciones.

        Args:
            force_check: Si es True, ignora el intervalo mínimo entre verificaciones
            notification_callback: Función a llamar cuando hay una actualización disponible,
                                   recibe (version, url, changelog)
        """
        # Guardar callback para notificaciones
        if notification_callback:
            self.notification_callback = notification_callback

        # Verificar si hay una verificación en curso
        if self.update_checker and self.update_checker.isRunning():
            return

        # Crear y configurar el verificador
        self.update_checker = UpdateChecker(force_check)

        # Conectar señales
        self.update_checker.update_available.connect(self._on_update_available)
        self.update_checker.check_failed.connect(self._on_check_failed)

        # Iniciar verificación
        self.update_checker.start()
        logger.info("Verificación de actualizaciones iniciada")

    def _on_update_available(self, version: str, url: str) -> None:
        """
        Manejador para cuando hay una actualización disponible.

        Args:
            version: Nueva versión disponible
            url: URL para descargar la actualización
        """
        logger.info(f"Actualización disponible: versión {version}")

        # Notificar a través del callback si está disponible
        if self.notification_callback:
            changelog = self._get_changelog(version)
            self.notification_callback(version, url, changelog)

    def _on_check_failed(self, error_message: str) -> None:
        """
        Manejador para cuando falla la verificación.

        Args:
            error_message: Mensaje de error
        """
        logger.warning(f"Error al verificar actualizaciones: {error_message}")

    def _get_changelog(self, version: str) -> str:
        """
        Obtiene el registro de cambios para una versión específica.

        Args:
            version: Versión para la que se quiere obtener el changelog

        Returns:
            str: Texto del changelog o mensaje informativo
        """
        try:
            # URL para el release específico
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/v{version}"

            headers = {
                'User-Agent': f'{APP_NAME}/{APP_VERSION}',
                'Accept': 'application/vnd.github.v3+json'
            }
            req = Request(url, headers=headers)

            with urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return data.get('body', 'No hay detalles disponibles para esta versión.')

            return "No se pudo obtener información de la nueva versión."

        except Exception as e:
            logger.error(f"Error al obtener changelog: {e}")
            return "No se pudo obtener información de la nueva versión."

    def open_download_page(self, url: str) -> None:
        """
        Abre la página de descarga en el navegador.

        Args:
            url: URL de la página de descarga
        """
        try:
            webbrowser.open(url)
            logger.info(f"Navegador abierto con URL: {url}")
        except Exception as e:
            logger.error(f"Error al abrir navegador: {e}")


# Alias para facilitar el acceso
def check_for_updates(force_check: bool = False,
                      notification_callback: Optional[Callable[[str, str, str], None]] = None) -> None:
    """
    Inicia la verificación de actualizaciones.

    Args:
        force_check: Si es True, ignora el intervalo mínimo entre verificaciones
        notification_callback: Función a llamar cuando hay una actualización disponible,
                               recibe (version, url, changelog)
    """
    UpdateManager.get_instance().check_for_updates(force_check, notification_callback)


def open_download_page(url: str) -> None:
    """
    Abre la página de descarga en el navegador.

    Args:
        url: URL de la página de descarga
    """
    UpdateManager.get_instance().open_download_page(url)