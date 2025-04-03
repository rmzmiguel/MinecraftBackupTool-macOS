"""
Widget para mostrar una lista de mundos de Minecraft.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QScrollArea, QCheckBox, QLabel
)
from PyQt6.QtCore import Qt, pyqtSignal

from app.views.world_item import WorldItemWidget
from app.utils.styles import (
    get_checkbox_style, get_world_count_label_style,
    get_selection_status_style, get_worlds_widget_style,
    get_world_list_scroll_area_style
)


class WorldListWidget(QWidget):
    """
    Widget que muestra una lista de mundos de Minecraft con
    opciones de selección y desplazamiento.

    Proporciona:
    - Visualización de mundos en una lista desplazable
    - Selección individual o masiva de mundos
    - Mantenimiento del estado de selección consistente
    """

    # Señal emitida cuando cambia cualquier selección
    selection_changed = pyqtSignal()

    def __init__(self, worlds, platform):
        """
        Inicializa el widget con una lista de mundos.

        Args:
            worlds: Lista de diccionarios con datos de mundos
            platform: Nombre de la plataforma (ej. "Java", "Bedrock")
        """
        super().__init__()
        self.worlds = worlds
        self.platform = platform
        self.world_items = []
        self.selected_worlds = []
        self.is_updating_selection = False  # Flag para prevenir recursión
        self.initUI()

    def initUI(self):
        """Configura la interfaz de usuario del widget."""
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Cabecera con checkbox "Seleccionar todo" y contador
        header_layout = QHBoxLayout()

        # Checkbox "Seleccionar todo"
        self.select_all_cb = QCheckBox("Seleccionar todo")
        self.select_all_cb.setStyleSheet(get_checkbox_style())
        self.select_all_cb.setTristate(True)  # Permitir estado intermedio
        self.select_all_cb.toggled.connect(self.toggle_all)
        header_layout.addWidget(self.select_all_cb)

        # Etiqueta con el número de mundos
        self.count_label = QLabel(f"{len(self.worlds)} mundos disponibles")
        self.count_label.setStyleSheet(get_world_count_label_style())
        header_layout.addWidget(self.count_label, alignment=Qt.AlignmentFlag.AlignRight)

        layout.addLayout(header_layout)

        # Área desplazable para la lista de mundos
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(get_world_list_scroll_area_style())

        # Widget contenedor para la lista de mundos
        worlds_widget = QWidget()
        worlds_widget.setStyleSheet(get_worlds_widget_style())
        worlds_layout = QVBoxLayout(worlds_widget)
        worlds_layout.setSpacing(8)
        worlds_layout.setContentsMargins(0, 0, 5, 0)  # Margen derecho para el scrollbar

        # Añadir cada mundo a la lista
        for world in self.worlds:
            world_item = WorldItemWidget(world)
            world_item.selection_changed.connect(self.update_selection)
            worlds_layout.addWidget(world_item)
            self.world_items.append(world_item)

        worlds_layout.addStretch()
        scroll_area.setWidget(worlds_widget)
        layout.addWidget(scroll_area)

        # Etiqueta de selección actual
        self.selection_status = QLabel("0 mundos seleccionados")
        self.selection_status.setStyleSheet(get_selection_status_style())
        self.selection_status.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.selection_status)

        self.setLayout(layout)

        # Actualizar el estado inicial
        self._update_selection_status()

    def update_selection(self, checked, world_data):
        """
        Actualiza la lista de mundos seleccionados.

        Args:
            checked: Estado de selección
            world_data: Datos del mundo
        """
        # Evitar actualizaciones recursivas
        if self.is_updating_selection:
            return

        # Crear una tupla con datos relevantes para backup/restore
        world_tuple = (world_data['path'], world_data['platform'], world_data['name'])

        # Actualizar lista de selección
        if checked and world_tuple not in self.selected_worlds:
            self.selected_worlds.append(world_tuple)
        elif not checked and world_tuple in self.selected_worlds:
            self.selected_worlds.remove(world_tuple)

        # Actualizar el estado de "Seleccionar todo" de manera segura
        self._update_select_all_state()

        # Actualizar etiqueta de estado
        self._update_selection_status()

        # Emitir señal de cambio
        self.selection_changed.emit()

    def _update_select_all_state(self):
        """
        Actualiza el estado del checkbox "Seleccionar todo" basado en las selecciones actuales.
        Previene recursión usando un flag.
        """
        self.is_updating_selection = True

        # Determinar si todos los mundos están seleccionados
        total_worlds = len(self.world_items)
        selected_count = len(self.selected_worlds)

        if selected_count == 0:
            # Ninguno seleccionado
            self.select_all_cb.setCheckState(Qt.CheckState.Unchecked)
        elif selected_count == total_worlds:
            # Todos seleccionados
            self.select_all_cb.setCheckState(Qt.CheckState.Checked)
        else:
            # Algunos seleccionados (estado parcial)
            self.select_all_cb.setCheckState(Qt.CheckState.PartiallyChecked)

        self.is_updating_selection = False

    def _update_selection_status(self):
        """Actualiza la etiqueta de estado con el número de mundos seleccionados."""
        count = len(self.selected_worlds)
        self.selection_status.setText(f"{count} mundo{'s' if count != 1 else ''} seleccionado{'s' if count != 1 else ''}")

    def toggle_all(self, checked):
        """
        Selecciona o deselecciona todos los mundos.

        Args:
            checked: True para seleccionar todos, False para deseleccionar
        """
        # Evitar actualizaciones recursivas
        if self.is_updating_selection:
            return

        self.is_updating_selection = True

        # Si estamos en estado parcial (tristate) y el usuario hace clic,
        # interpretamos esto como un deseo de seleccionar todo
        if self.select_all_cb.checkState() == Qt.CheckState.PartiallyChecked:
            checked = True
            self.select_all_cb.setCheckState(Qt.CheckState.Checked)

        # Limpiar selecciones actuales
        self.selected_worlds = []

        # Actualizar cada item
        for item in self.world_items:
            item.set_selected(checked)
            if checked:
                world_data = item.world_data
                self.selected_worlds.append((
                    world_data['path'],
                    world_data['platform'],
                    world_data['name']
                ))

        # Actualizar etiqueta de estado
        self._update_selection_status()

        self.is_updating_selection = False

        # Emitir señal de cambio
        self.selection_changed.emit()

    def get_selected_worlds(self):
        """
        Obtiene la lista de mundos seleccionados.

        Returns:
            list: Lista de tuplas (path, platform, name) para cada mundo seleccionado
        """
        return self.selected_worlds