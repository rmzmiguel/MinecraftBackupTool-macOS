"""
Widget para mostrar un estado vacío cuando no hay mundos disponibles.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon
from app.utils.styles import get_empty_state_style


class EmptyStateWidget(QWidget):
    """
    Widget que muestra un mensaje informativo cuando no hay mundos disponibles.
    Proporciona información sobre posibles acciones a realizar.
    """

    # Señal para indicar que se solicitó restaurar mundos
    restore_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Inicializa el widget de estado vacío."""
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        """Configura la interfaz de usuario del widget."""
        empty_style = get_empty_state_style()
        self.setStyleSheet(empty_style)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Icono informativo
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Intentar cargar un icono (Minecraft relacionado o un ícono de información)
        icon = QIcon("resources/icon.png")
        if not icon.isNull():
            pixmap = icon.pixmap(128, 128)
            icon_label.setPixmap(pixmap)
            layout.addWidget(icon_label)

        # Título
        title_label = QLabel("No se encontraron mundos de Minecraft")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setProperty("role", "title")
        layout.addWidget(title_label)

        # Mensaje explicativo
        message_label = QLabel(
            "No se han detectado mundos de Minecraft en las ubicaciones habituales.\n"
            "Esto puede deberse a que:"
        )
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setProperty("role", "message")
        layout.addWidget(message_label)

        # Lista de posibles razones
        reasons_layout = QVBoxLayout()
        reasons = [
            "Minecraft no está instalado en este equipo",
            "Aún no has creado ningún mundo en Minecraft",
            "Minecraft está instalado en una ubicación no estándar",
            "Los permisos de acceso a la carpeta de Minecraft son insuficientes"
        ]

        for reason in reasons:
            reason_label = QLabel(f"• {reason}")
            reason_label.setProperty("role", "reason")
            reason_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            reasons_layout.addWidget(reason_label)

        # Centrar la lista de razones
        reasons_container = QWidget()
        reasons_container.setLayout(reasons_layout)
        layout.addWidget(reasons_container, alignment=Qt.AlignmentFlag.AlignCenter)

        # Mensaje de solución
        solution_label = QLabel(
            "Puedes restaurar mundos desde un respaldo existente o verificar la configuración\n"
            "para añadir ubicaciones personalizadas donde buscar mundos."
        )
        solution_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        solution_label.setProperty("role", "solution")
        layout.addWidget(solution_label)

        # Botón de restauración
        button_layout = QHBoxLayout()
        restore_button = QPushButton("Restaurar mundos desde respaldo")
        restore_button.clicked.connect(self.restore_requested.emit)
        button_layout.addWidget(restore_button, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addLayout(button_layout)
        layout.addStretch()