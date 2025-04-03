"""
Widget para representar un mundo individual en la interfaz de usuario.
"""

import os
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel, QCheckBox
from PyQt6.QtGui import QPixmap, QImage, QColor, QCursor
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from app.utils.styles import (
    get_world_item_style, get_world_icon_container_style,
    get_world_icon_label_style, get_world_icon_mask_style,
    get_world_content_container_style, get_world_name_label_style,
    get_world_path_label_style, get_world_platform_label_style,
    get_world_checkbox_style
)


class WorldItemWidget(QFrame):
    """
    Widget personalizado para mostrar un mundo de Minecraft con su
    icono, información y casilla de selección.
    """

    # Señal emitida cuando cambia el estado de selección
    selection_changed = pyqtSignal(bool, dict)

    def __init__(self, world_data):
        """
        Inicializa el widget con los datos del mundo.

        Args:
            world_data: Diccionario con datos del mundo ('path', 'name', 'platform', 'icon')
        """
        super().__init__()
        self.world_data = world_data
        self.initUI()

    def initUI(self):
        """Configura la interfaz de usuario del widget."""
        # Configuración principal del widget
        self.setObjectName("worldItem")
        self.setFixedHeight(100)
        self.setStyleSheet(get_world_item_style())

        # Habilitar seguimiento del mouse para efectos hover
        self.setMouseTracking(True)

        # Hacer que el widget sea clickeable
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))

        # Layout principal sin márgenes
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ---- SECCIÓN DE ICONO ----
        # Contenedor del icono con recorte en las esquinas izquierdas
        icon_container = QFrame()
        icon_container.setObjectName("iconContainer")
        icon_container.setFixedWidth(100)  # Ancho fijo alineado con la altura del widget
        icon_container.setStyleSheet(get_world_icon_container_style())

        # Layout sin márgenes para el icono
        icon_layout = QHBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)

        # Creación del QLabel para la imagen con recorte
        icon_label = QLabel()
        icon_label.setObjectName("iconLabel")
        icon_label.setFixedSize(100, 100)  # Tamaño fijo alineado con el contenedor
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(get_world_icon_label_style())

        # Establecer una máscara para recortar la imagen exactamente
        # La propiedad overflow:hidden se aplica mediante una QFrame contenedora
        icon_mask = QFrame(icon_label)
        icon_mask.setObjectName("iconMask")
        icon_mask.setFixedSize(100, 100)
        icon_mask.setStyleSheet(get_world_icon_mask_style())

        # Establecer el icono
        if self.world_data['icon'] and os.path.exists(self.world_data['icon']):
            pixmap = QPixmap(self.world_data['icon'])
            # Escalar manteniendo la proporción
            pixmap = pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                  Qt.TransformationMode.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setScaledContents(True)
        else:
            # Icono por defecto según la plataforma
            default_icon_path = f"resources/icons/{self.world_data['platform'].lower()}_icon.png"

            if os.path.exists(default_icon_path):
                default_icon = QPixmap(default_icon_path)
                default_icon = default_icon.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio,
                                                  Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(default_icon)
            else:
                # Si no hay icono, crear uno coloreado
                img = QImage(80, 80, QImage.Format.Format_ARGB32)
                if self.world_data['platform'] == 'Java':
                    img.fill(QColor(235, 64, 52))  # Rojo para Java
                else:
                    img.fill(QColor(52, 152, 219))  # Azul para Bedrock
                default_icon = QPixmap.fromImage(img)
                icon_label.setPixmap(default_icon)

            icon_label.setScaledContents(True)

        # Añadir el icono al layout
        icon_layout.addWidget(icon_label)
        layout.addWidget(icon_container)

        # ---- SECCIÓN DE CONTENIDO (INFORMACIÓN) ----
        # Contenedor para texto y checkbox
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_container.setStyleSheet(get_world_content_container_style())

        # Layout para el contenedor de información
        content_layout = QHBoxLayout(content_container)
        content_layout.setContentsMargins(15, 10, 15, 10)

        # Layout vertical para información del mundo
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        # Nombre del mundo
        name_label = QLabel(self.world_data['name'])
        name_label.setStyleSheet(get_world_name_label_style())
        info_layout.addWidget(name_label)

        # Ruta del mundo (acortada si es muy larga)
        path_text = self.world_data['path']
        if len(path_text) > 80:
            path_start = path_text[:40]
            path_end = path_text[-40:]
            path_text = f"{path_start}...{path_end}"

        path_label = QLabel(path_text)
        path_label.setStyleSheet(get_world_path_label_style())
        path_label.setWordWrap(True)
        info_layout.addWidget(path_label)

        # Información de la plataforma
        platform_label = QLabel(f"Platform: {self.world_data['platform']}")
        platform_label.setStyleSheet(get_world_platform_label_style())
        info_layout.addWidget(platform_label)

        # Espacio flexible para alinear el contenido
        info_layout.addStretch()

        # Añadir la información al layout de contenido
        content_layout.addLayout(info_layout, stretch=1)

        # ---- SECCIÓN DE CHECKBOX ----
        # Checkbox de selección
        self.checkbox = QCheckBox()
        self.checkbox.setStyleSheet(get_world_checkbox_style())
        self.checkbox.toggled.connect(self._on_selection_changed)
        content_layout.addWidget(self.checkbox, alignment=Qt.AlignmentFlag.AlignCenter)

        # Añadir el contenedor de contenido al layout principal
        layout.addWidget(content_container, stretch=1)

    def mousePressEvent(self, event):
        """
        Manejador para eventos de clic en el widget.
        Alterna el estado del checkbox cuando se hace clic en cualquier parte del widget.

        Args:
            event: Evento de ratón
        """
        # Alternar el estado del checkbox (excepto si el clic fue directamente en el checkbox)
        if not self.checkbox.underMouse():
            self.checkbox.setChecked(not self.checkbox.isChecked())

        # Procesamiento estándar del evento
        super().mousePressEvent(event)

    def _on_selection_changed(self, checked):
        """
        Manejador para cambios en el estado del checkbox.

        Args:
            checked: Estado actual del checkbox
        """
        self.selection_changed.emit(checked, self.world_data)

    def is_selected(self):
        """
        Comprueba si este mundo está seleccionado.

        Returns:
            bool: True si está seleccionado, False en caso contrario
        """
        return self.checkbox.isChecked()

    def set_selected(self, selected):
        """
        Establece el estado de selección.

        Args:
            selected: True para seleccionar, False para deseleccionar
        """
        self.checkbox.setChecked(selected)