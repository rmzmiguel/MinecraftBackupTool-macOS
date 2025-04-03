"""
Ventana principal de la aplicación Minecraft Backup Tool.
"""

import os
import sys  # <- nuevo
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFileDialog, QMessageBox,
    QProgressBar, QTabWidget, QSplashScreen, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QFont, QColor, QImage, QPainter

from app.models.world_registry import WorldRegistry
from app.views.world_list import WorldListWidget
from app.controllers.backup_controller import BackupController
from app.controllers.restore_controller import RestoreController
from app.utils.styles import (
    get_main_window_style, get_button_style, get_tab_style,
    get_label_style, get_title_label_style, get_message_box_style
)
from .BackgroundBubbles import BackgroundBubbles
from app.views.BackupProgressDialog import BackupProgressDialog


def get_resource_path(relative_path):
    """Ruta compatible con PyInstaller y modo desarrollo"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'resources'))
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación Minecraft Backup Tool.
    Gestiona la interfaz de usuario y coordina las operaciones.
    """

    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__()
        self.worlds_by_platform = {}
        self.backup_controller = BackupController()
        self.restore_controller = RestoreController()

        self.initUI()

        WorldRegistry.initialize()
        self.load_worlds()

    def initUI(self):
        """Configura la interfaz de usuario de la ventana principal."""
        self.setWindowTitle("Minecraft Backup Tool")
        self.setMinimumSize(1200, 800)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Ícono de la ventana (funciona en el .exe y en el IDE)
        app_icon_path = get_resource_path("appgenius_icon.ico")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))

        self.setStyleSheet(get_main_window_style() + get_button_style() + get_tab_style() + get_label_style())

        central_widget = QWidget()
        central_widget.setObjectName("mainBackground")
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(13)

        self.background_bubbles = BackgroundBubbles(central_widget)
        self.background_bubbles.setGeometry(0, 0, self.width(), self.height())

        header_layout = QHBoxLayout()
        logo_label = QLabel("Minecraft Backup Tool")
        logo_label.setStyleSheet(get_title_label_style())
        header_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignLeft)

        about_button = QPushButton("Acerca de")
        about_button.setFixedWidth(144)
        about_button.clicked.connect(self.show_about)
        header_layout.addWidget(about_button, alignment=Qt.AlignmentFlag.AlignRight)

        main_layout.addLayout(header_layout)

        self.tabs = QTabWidget()
        self.tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        main_layout.addWidget(self.tabs)

        button_layout = QHBoxLayout()

        self.backup_button = QPushButton("Respaldar mundos seleccionados")
        self.backup_button.setIcon(QIcon("resources/backup_icon.png"))
        self.backup_button.clicked.connect(self.backup_worlds)
        button_layout.addWidget(self.backup_button)

        self.restore_button = QPushButton("Restaurar mundos")
        self.restore_button.setIcon(QIcon("resources/restore_icon.png"))
        self.restore_button.clicked.connect(self.restore_worlds)
        button_layout.addWidget(self.restore_button)

        main_layout.addLayout(button_layout)

        self.progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(True)
        self.progress_layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("Listo")
        self.progress_layout.addWidget(self.progress_label)

        main_layout.addLayout(self.progress_layout)

        self.progress_bar.hide()
        self.progress_label.hide()

        self.statusBar().showMessage("Listo para respaldar o restaurar mundos de Minecraft")

        self._ensure_resources()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'background_bubbles'):
            self.background_bubbles.setGeometry(0, 0, self.width(), self.height())

    def _ensure_resources(self):
        if not getattr(sys, 'frozen', False):
            os.makedirs("resources/icons", exist_ok=True)

            self._create_placeholder_icon("resources/icons/app_icon.png", QColor(116, 199, 236))
            self._create_placeholder_icon("resources/icons/java_icon.png", QColor(235, 64, 52))
            self._create_placeholder_icon("resources/icons/bedrock_icon.png", QColor(52, 152, 219))
            self._create_placeholder_icon("resources/icons/backup_icon.png", QColor(255, 255, 255), size=(24, 24))
            self._create_placeholder_icon("resources/icons/restore_icon.png", QColor(255, 255, 255), size=(24, 24))

    def _create_placeholder_icon(self, path, color, size=(64, 64)):
        if not os.path.exists(path):
            img = QImage(size[0], size[1], QImage.Format.Format_ARGB32)
            img.fill(color)
            QPixmap.fromImage(img).save(path)

    def load_worlds(self):
        self.statusBar().showMessage("Buscando mundos de Minecraft...")
        self.worlds_by_platform = WorldRegistry.get_all_worlds()
        self.tabs.clear()
        total_worlds = sum(len(worlds) for worlds in self.worlds_by_platform.values())

        if total_worlds == 0:
            from app.views.empty_state import EmptyStateWidget
            empty_state = EmptyStateWidget()
            empty_state.restore_requested.connect(self.restore_worlds)

            empty_tab = QWidget()
            empty_layout = QVBoxLayout(empty_tab)
            empty_layout.addWidget(empty_state)

            self.tabs.addTab(empty_tab, "Sin mundos disponibles")
            self.statusBar().showMessage("No se encontraron mundos de Minecraft")
            self.backup_button.setEnabled(False)
        else:
            for platform, worlds in self.worlds_by_platform.items():
                if worlds:
                    platform_tab = QWidget()
                    platform_layout = QVBoxLayout(platform_tab)
                    worlds_list = WorldListWidget(worlds, platform)
                    platform_layout.addWidget(worlds_list)
                    count_label = QLabel(f"Encontrados {len(worlds)} mundos de {platform}")
                    count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
                    platform_layout.addWidget(count_label)

                    setattr(self, f"{platform.lower()}_list", worlds_list)
                    self.tabs.addTab(platform_tab, f"{platform} Edition")

            self.backup_button.setEnabled(True)
            self.statusBar().showMessage(f"Encontrados {total_worlds} mundos de Minecraft")

    def get_selected_worlds(self):
        selected_worlds = []
        for platform, worlds in self.worlds_by_platform.items():
            list_widget_name = f"{platform.lower()}_list"
            if hasattr(self, list_widget_name) and worlds:
                list_widget = getattr(self, list_widget_name)
                selected_worlds.extend(list_widget.get_selected_worlds())
        return selected_worlds

    def backup_worlds(self):
        selected_worlds = self.get_selected_worlds()
        if not selected_worlds:
            QMessageBox.warning(self, "Sin selección", "Por favor, selecciona al menos un mundo para respaldar.")
            return

        destination = QFileDialog.getExistingDirectory(self, "Seleccionar destino del respaldo")
        if not destination:
            return

        self.progress_dialog = BackupProgressDialog(self, "respaldo")
        self.backup_controller.backup_worlds(
            selected_worlds,
            destination,
            self.progress_dialog.update_progress,
            self.operation_finished
        )
        self.progress_dialog.exec()

    def restore_worlds(self):
        zip_file, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de respaldo",
            "",
            "Archivos ZIP (*.zip)"
        )

        if not zip_file:
            return

        self.progress_dialog = BackupProgressDialog(self, "restauración")
        self.restore_controller.restore_worlds(
            zip_file,
            self.progress_dialog.update_progress,
            self.operation_finished
        )
        self.progress_dialog.exec()

    def operation_finished(self, success, message):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.complete_operation()
        self.statusBar().showMessage(message)

        if success:
            self.load_worlds()
        else:
            QMessageBox.critical(self, "Error", message)

    def show_about(self):
        about_text = """
        <h2>Minecraft Backup Tool</h2>
        <p>Una herramienta moderna y multiplataforma para respaldar y restaurar tus mundos de Minecraft.</p>
        <p>Características:</p>
        <ul>
            <li>Soporte para ediciones Java y Bedrock</li>
            <li>Detección automática de mundos</li>
            <li>Vista previa de los mundos</li>
            <li>Organización por plataformas</li>
        </ul>
        <p><small>Versión 1.0.0</small><p><small>Made by Miguel Ramírez</small></p></p>
        """

        about_box = QMessageBox(self)
        about_box.setWindowTitle("Acerca de Minecraft Backup Tool")
        about_box.setText(about_text)
        about_box.setIcon(QMessageBox.Icon.Information)
        about_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        about_box.setStyleSheet(get_message_box_style())
        about_box.exec()
