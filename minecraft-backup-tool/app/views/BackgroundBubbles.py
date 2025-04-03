import os
import sys
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtCore import Qt


def get_resource_path(relative_path):
    """Devuelve la ruta absoluta al archivo, compatible con PyInstaller"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, "resources", relative_path)


class BackgroundBubbles(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # Cargar las imágenes con la ruta correcta
        self.blue_aurora = QPixmap(get_resource_path("aurora-blue.png"))
        self.pink_aurora = QPixmap(get_resource_path("aurora-pink.png"))

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        width = self.width()
        height = self.height()

        scale_factor = 0.89
        scaled_blue = self.blue_aurora.scaled(
            int(width * scale_factor),
            int(height * scale_factor),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        scaled_pink = self.pink_aurora.scaled(
            int(width * scale_factor),
            int(height * scale_factor),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        painter.drawPixmap(0, 0, scaled_blue)
        painter.drawPixmap(width - scaled_pink.width(), height - scaled_pink.height(), scaled_pink)
