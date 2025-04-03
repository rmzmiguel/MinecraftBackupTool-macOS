"""
Diálogo de configuración para la aplicación.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QCheckBox, QComboBox, QPushButton,
    QFileDialog, QSpinBox, QListWidget, QListWidgetItem,
    QGroupBox, QFormLayout, QDialogButtonBox, QMessageBox,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize

# Importar utilidades
try:
    from app.utils.config import get_config
    from app.utils.i18n import get_text
    from app.utils.styles import get_dialog_style
except ImportError:
    # Fallbacks para pruebas
    def get_config():
        class MockConfig:
            def get(self, key, default=None):
                return default

            def set(self, key, value):
                pass

        return MockConfig()


    def get_text(key, default=None):
        return default or key


    def get_dialog_style():
        return ""

# Configurar logger
logger = logging.getLogger("SettingsDialog")


class PathListWidget(QWidget):
    """
    Widget para gestionar una lista de rutas personalizadas.
    """

    # Señal emitida cuando cambia la lista
    paths_changed = pyqtSignal(list)

    def __init__(self, paths: List[str] = None, parent=None):
        """
        Inicializa el widget de lista de rutas.

        Args:
            paths: Lista inicial de rutas
            parent: Widget padre
        """
        super().__init__(parent)
        self.paths = paths or []
        self.initUI()

    def initUI(self):
        """Configura la interfaz de usuario del widget."""
        layout = QVBoxLayout(self)

        # Lista de rutas
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        layout.addWidget(self.list_widget)

        # Botones para gestionar la lista
        buttons_layout = QHBoxLayout()

        self.add_button = QPushButton("Añadir ruta")
        self.add_button.clicked.connect(self.add_path)
        buttons_layout.addWidget(self.add_button)

        self.remove_button = QPushButton("Eliminar seleccionada")
        self.remove_button.clicked.connect(self.remove_path)
        self.remove_button.setEnabled(False)  # Deshabilitar hasta que se seleccione una ruta
        buttons_layout.addWidget(self.remove_button)

        layout.addLayout(buttons_layout)

        # Conectar señal de selección para habilitar/deshabilitar botón de eliminar
        self.list_widget.itemSelectionChanged.connect(self.update_remove_button)

        # Cargar rutas iniciales
        self.load_paths(self.paths)

    def load_paths(self, paths: List[str]):
        """
        Carga una lista de rutas en el widget.

        Args:
            paths: Lista de rutas a cargar
        """
        self.list_widget.clear()
        for path in paths:
            self.list_widget.addItem(path)

    def get_paths(self) -> List[str]:
        """
        Obtiene la lista actual de rutas.

        Returns:
            List[str]: Lista de rutas
        """
        paths = []
        for i in range(self.list_widget.count()):
            paths.append(self.list_widget.item(i).text())
        return paths

    def add_path(self):
        """Abre un diálogo para seleccionar una nueva ruta."""
        directory = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de mundos"
        )

        if directory:
            # Verificar si ya existe en la lista
            for i in range(self.list_widget.count()):
                if self.list_widget.item(i).text() == directory:
                    # Ya existe, mostrar mensaje
                    QMessageBox.information(
                        self, "Ruta duplicada",
                        "Esta carpeta ya está en la lista."
                    )
                    return

            # Añadir a la lista
            self.list_widget.addItem(directory)

            # Emitir señal de cambio
            self.paths_changed.emit(self.get_paths())

    def remove_path(self):
        """Elimina la ruta seleccionada de la lista."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            for item in selected_items:
                self.list_widget.takeItem(self.list_widget.row(item))

            # Emitir señal de cambio
            self.paths_changed.emit(self.get_paths())

    def update_remove_button(self):
        """Actualiza el estado del botón de eliminar según la selección."""
        self.remove_button.setEnabled(len(self.list_widget.selectedItems()) > 0)


class SettingsDialog(QDialog):
    """
    Diálogo para configurar preferencias de la aplicación.
    """

    # Señal emitida cuando se aplican cambios
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        """
        Inicializa el diálogo de configuración.

        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.config = get_config()
        self.language_options = {
            "es": "Español",
            "en": "English",
            "fr": "Français",
            "de": "Deutsch",
            "pt": "Português",
            "it": "Italiano"
        }
        self.theme_options = {
            "dark": "Oscuro",
            "light": "Claro"
        }
        self.initUI()
        self.loadSettings()

    def initUI(self):
        """Configura la interfaz de usuario del diálogo."""
        self.setWindowTitle("Configuración")
        self.setMinimumSize(700, 500)

        # Aplicar estilos
        self.setStyleSheet(get_dialog_style())

        # Layout principal
        main_layout = QVBoxLayout(self)

        # Tabs de configuración
        self.tabs = QTabWidget()

        # Pestaña General
        general_tab = QWidget()
        self.setup_general_tab(general_tab)
        self.tabs.addTab(general_tab, "General")

        # Pestaña Ubicaciones
        locations_tab = QWidget()
        self.setup_locations_tab(locations_tab)
        self.tabs.addTab(locations_tab, "Ubicaciones")

        # Pestaña Respaldos
        backups_tab = QWidget()
        self.setup_backups_tab(backups_tab)
        self.tabs.addTab(backups_tab, "Respaldos")

        # Pestaña Avanzado
        advanced_tab = QWidget()
        self.setup_advanced_tab(advanced_tab)
        self.tabs.addTab(advanced_tab, "Avanzado")

        main_layout.addWidget(self.tabs)

        # Botones de acción
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Reset
        )
        button_box.accepted.connect(self.save_settings)
        button_box.rejected.connect(self.reject)

        # Configurar el botón de reset
        reset_button = button_box.button(QDialogButtonBox.StandardButton.Reset)
        reset_button.setText("Restablecer predeterminados")
        reset_button.clicked.connect(self.reset_to_defaults)

        main_layout.addWidget(button_box)

    def setup_general_tab(self, tab):
        """
        Configura la pestaña General.

        Args:
            tab: Widget de la pestaña
        """
        layout = QVBoxLayout(tab)

        # Grupo Apariencia
        appearance_group = QGroupBox("Apariencia")
        appearance_layout = QFormLayout(appearance_group)

        # Tema
        self.theme_combo = QComboBox()
        for key, value in self.theme_options.items():
            self.theme_combo.addItem(value, key)
        appearance_layout.addRow("Tema:", self.theme_combo)

        # Idioma
        self.language_combo = QComboBox()
        for key, value in self.language_options.items():
            self.language_combo.addItem(value, key)
        appearance_layout.addRow("Idioma:", self.language_combo)

        # Opciones de UI
        self.show_splash_cb = QCheckBox("Mostrar pantalla de inicio")
        appearance_layout.addRow("", self.show_splash_cb)

        self.show_tooltips_cb = QCheckBox("Mostrar descripciones emergentes")
        appearance_layout.addRow("", self.show_tooltips_cb)

        layout.addWidget(appearance_group)

        # Grupo Actualizaciones
        updates_group = QGroupBox("Actualizaciones")
        updates_layout = QFormLayout(updates_group)

        self.check_updates_cb = QCheckBox("Buscar actualizaciones automáticamente")
        updates_layout.addRow("", self.check_updates_cb)

        self.check_now_button = QPushButton("Buscar actualizaciones ahora")
        updates_layout.addRow("", self.check_now_button)

        layout.addWidget(updates_group)

        # Espacio flexible
        layout.addStretch()

    def setup_locations_tab(self, tab):
        """
        Configura la pestaña Ubicaciones.

        Args:
            tab: Widget de la pestaña
        """
        layout = QVBoxLayout(tab)

        # Grupo Java Edition
        java_group = QGroupBox("Minecraft Java Edition")
        java_layout = QVBoxLayout(java_group)

        java_label = QLabel("Rutas adicionales donde buscar mundos:")
        java_layout.addWidget(java_label)

        self.java_paths_widget = PathListWidget(
            self.config.get("custom_paths.java", [])
        )
        java_layout.addWidget(self.java_paths_widget)

        layout.addWidget(java_group)

        # Grupo Bedrock Edition
        bedrock_group = QGroupBox("Minecraft Bedrock Edition")
        bedrock_layout = QVBoxLayout(bedrock_group)

        bedrock_label = QLabel("Rutas adicionales donde buscar mundos:")
        bedrock_layout.addWidget(bedrock_label)

        self.bedrock_paths_widget = PathListWidget(
            self.config.get("custom_paths.bedrock", [])
        )
        bedrock_layout.addWidget(self.bedrock_paths_widget)

        layout.addWidget(bedrock_group)

    def setup_backups_tab(self, tab):
        """
        Configura la pestaña Respaldos.

        Args:
            tab: Widget de la pestaña
        """
        layout = QVBoxLayout(tab)

        # Grupo Ubicación predeterminada
        location_group = QGroupBox("Ubicación predeterminada")
        location_layout = QHBoxLayout(location_group)

        self.default_backup_path = QLineEdit()
        self.default_backup_path.setReadOnly(True)
        location_layout.addWidget(self.default_backup_path)

        browse_button = QPushButton("Examinar...")
        browse_button.clicked.connect(self.browse_backup_path)
        location_layout.addWidget(browse_button)

        layout.addWidget(location_group)

        # Grupo Opciones de respaldo
        options_group = QGroupBox("Opciones de respaldo")
        options_layout = QFormLayout(options_group)

        # Nivel de compresión
        self.compress_level = QSpinBox()
        self.compress_level.setRange(0, 9)
        self.compress_level.setToolTip("0 = sin compresión, 9 = máxima compresión")
        options_layout.addRow("Nivel de compresión:", self.compress_level)

        # Máximo de respaldos
        self.max_backups = QSpinBox()
        self.max_backups.setRange(0, 100)
        self.max_backups.setToolTip("0 = sin límite")
        options_layout.addRow("Número máximo de respaldos:", self.max_backups)

        # Incluir capturas de pantalla
        self.include_screenshots = QCheckBox()
        options_layout.addRow("Incluir capturas de pantalla:", self.include_screenshots)

        layout.addWidget(options_group)

        # Grupo Respaldo automático
        auto_group = QGroupBox("Respaldo automático")
        auto_layout = QFormLayout(auto_group)

        # Intervalo en días
        self.auto_backup_days = QSpinBox()
        self.auto_backup_days.setRange(0, 30)
        self.auto_backup_days.setToolTip("0 = desactivado")
        auto_layout.addRow("Intervalo (días):", self.auto_backup_days)

        layout.addWidget(auto_group)

        # Espacio flexible
        layout.addStretch()

    def setup_advanced_tab(self, tab):
        """
        Configura la pestaña Avanzado.

        Args:
            tab: Widget de la pestaña
        """
        layout = QVBoxLayout(tab)

        # Grupo Proveedores
        providers_group = QGroupBox("Proveedores de mundos")
        providers_layout = QVBoxLayout(providers_group)

        self.java_provider_cb = QCheckBox("Java Edition")
        providers_layout.addWidget(self.java_provider_cb)

        self.bedrock_provider_cb = QCheckBox("Bedrock Edition")
        providers_layout.addWidget(self.bedrock_provider_cb)

        self.prism_provider_cb = QCheckBox("PrismLauncher")
        providers_layout.addWidget(self.prism_provider_cb)

        layout.addWidget(providers_group)

        # Grupo Diagnóstico
        diagnostic_group = QGroupBox("Diagnóstico")
        diagnostic_layout = QVBoxLayout(diagnostic_group)

        view_log_button = QPushButton("Ver archivos de registro")
        view_log_button.clicked.connect(self.view_logs)
        diagnostic_layout.addWidget(view_log_button)

        layout.addWidget(diagnostic_group)

        # Espacio flexible
        layout.addStretch()

    def loadSettings(self):
        """Carga la configuración actual en los controles del diálogo."""
        # Pestaña General

        # Tema
        theme = self.config.get("appearance.theme", "dark")
        index = self.theme_combo.findData(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)

        # Idioma
        language = self.config.get("appearance.language", "es")
        index = self.language_combo.findData(language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)

        # Opciones de UI
        self.show_splash_cb.setChecked(self.config.get("appearance.show_splash", True))
        self.show_tooltips_cb.setChecked(self.config.get("appearance.show_tooltips", True))

        # Actualizaciones
        self.check_updates_cb.setChecked(self.config.get("updates.check_updates", True))

        # Pestaña Respaldos

        # Ruta predeterminada
        self.default_backup_path.setText(self.config.get("backups.default_destination", ""))

        # Opciones de respaldo
        self.compress_level.setValue(self.config.get("backups.compress_level", 6))
        self.max_backups.setValue(self.config.get("backups.max_backups", 10))
        self.include_screenshots.setChecked(self.config.get("backups.include_screenshots", False))

        # Respaldo automático
        self.auto_backup_days.setValue(self.config.get("backups.auto_backup_interval_days", 0))

        # Pestaña Avanzado

        # Proveedores
        self.java_provider_cb.setChecked(self.config.get("providers.java", True))
        self.bedrock_provider_cb.setChecked(self.config.get("providers.bedrock", True))
        self.prism_provider_cb.setChecked(self.config.get("providers.prism_launcher", False))

    def save_settings(self):
        """Guarda la configuración modificada."""
        # Pestaña General

        # Tema
        theme = self.theme_combo.currentData()
        self.config.set("appearance.theme", theme)

        # Idioma
        language = self.language_combo.currentData()
        self.config.set("appearance.language", language)

        # Opciones de UI
        self.config.set("appearance.show_splash", self.show_splash_cb.isChecked())
        self.config.set("appearance.show_tooltips", self.show_tooltips_cb.isChecked())

        # Actualizaciones
        self.config.set("updates.check_updates", self.check_updates_cb.isChecked())

        # Pestaña Ubicaciones

        # Rutas Java
        self.config.set("custom_paths.java", self.java_paths_widget.get_paths())

        # Rutas Bedrock
        self.config.set("custom_paths.bedrock", self.bedrock_paths_widget.get_paths())

        # Pestaña Respaldos

        # Ruta predeterminada
        self.config.set("backups.default_destination", self.default_backup_path.text())

        # Opciones de respaldo
        self.config.set("backups.compress_level", self.compress_level.value())
        self.config.set("backups.max_backups", self.max_backups.value())
        self.config.set("backups.include_screenshots", self.include_screenshots.isChecked())

        # Respaldo automático
        self.config.set("backups.auto_backup_interval_days", self.auto_backup_days.value())

        # Pestaña Avanzado

        # Proveedores
        self.config.set("providers.java", self.java_provider_cb.isChecked())
        self.config.set("providers.bedrock", self.bedrock_provider_cb.isChecked())
        self.config.set("providers.prism_launcher", self.prism_provider_cb.isChecked())

        # Guardar configuración
        if self.config.save():
            logger.info("Configuración guardada correctamente")

            # Emitir señal de cambio
            self.settings_changed.emit()

            # Cerrar diálogo
            self.accept()
        else:
            QMessageBox.warning(
                self, "Error",
                "No se pudo guardar la configuración. Consulta los logs para más información."
            )

    def browse_backup_path(self):
        """Abre un diálogo para seleccionar la carpeta de respaldo predeterminada."""
        directory = QFileDialog.getExistingDirectory(
            self, "Seleccionar carpeta de respaldo predeterminada",
            self.default_backup_path.text()
        )

        if directory:
            self.default_backup_path.setText(directory)

    def view_logs(self):
        """Abre el explorador de archivos en la carpeta de logs."""
        import subprocess
        import sys

        # Obtener la carpeta de logs
        log_dir = os.path.join(self.config.config_dir(), "logs")

        # Verificar si existe
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Abrir la carpeta según el sistema operativo
        try:
            if sys.platform == 'win32':
                os.startfile(log_dir)
            elif sys.platform == 'darwin':  # macOS
                subprocess.run(['open', log_dir])
            else:  # Linux
                subprocess.run(['xdg-open', log_dir])
        except Exception as e:
            logger.error(f"Error al abrir carpeta de logs: {e}")
            QMessageBox.warning(
                self, "Error",
                f"No se pudo abrir la carpeta de logs: {str(e)}"
            )

    def reset_to_defaults(self):
        """Restablece la configuración a valores predeterminados."""
        # Pedir confirmación
        reply = QMessageBox.question(
            self, "Restablecer configuración",
            "¿Seguro que deseas restablecer toda la configuración a valores predeterminados?\n\n"
            "Esta acción no puede deshacerse.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Restablecer configuración
            self.config.reset()

            # Recargar controles
            self.loadSettings()

            # Informar al usuario
            QMessageBox.information(
                self, "Configuración restablecida",
                "La configuración se ha restablecido a valores predeterminados."
            )