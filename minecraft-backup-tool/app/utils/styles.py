"""
Utilidades para manejar estilos de la interfaz de usuario.
"""

import os

# Color Scheme - Colores principales de la UI
BACKGROUND_COLOR = "#18181B"     # Fondo principal
TEXT_COLOR = "#D1D5DB"           # Texto general
TITLE_COLOR = "#F4F4F5"          # Títulos/Encabezados

# Color Scheme - Botones
BUTTON_BG_COLOR = "#D4D4D8"       # Fondo de botones
BUTTON_TEXT_COLOR = "#09090B"     # Texto de botones
BUTTON_HOVER_COLOR = "#a1a1aa"    # Hover de botones
BUTTON_PRESSED_COLOR = "#e4e4e7"  # Botones presionados
BUTTON_DISABLED_BG_COLOR = "rgba(212, 212, 216, .13)"  # Fondo de botones deshabilitados
BUTTON_DISABLED_TEXT_COLOR = TEXT_COLOR  # Texto de botones deshabilitados

# Color Scheme - Tabs
TAB_BG_COLOR = "rgba(212, 212, 216, .13)"  # Fondo de pestañas
TAB_TEXT_COLOR = "#D4D4D8"        # Texto de pestañas
TAB_SELECTED_BG_COLOR = "#6B7280"  # Fondo de pestaña seleccionada
TAB_SELECTED_TEXT_COLOR = "#D4D4D8"  # Texto de pestaña seleccionada

# Color Scheme - Otros elementos
FRAME_BG_COLOR = "transparent"
PROGRESS_BAR_BG_COLOR = "#2c2c2c"
PROGRESS_BAR_CHUNK_COLOR = "#74c7ec"  # Azul del progreso normal
PROGRESS_BAR_SUCCESS_COLOR = "#05C17C"  # Verde para éxito
PROGRESS_BAR_INFO_COLOR = "#356BFC"     # Azul alternativo para información

# Color Scheme - World Item
WORLD_ITEM_BORDER_COLOR = "#313244"
WORLD_ITEM_HOVER_BORDER_COLOR = "#74c7ec"
WORLD_ITEM_HOVER_BG_COLOR = "rgba(116, 199, 236, 0.05)"
WORLD_ITEM_ICON_BG_COLOR = "#181818"
WORLD_NAME_COLOR = "white"
WORLD_PATH_COLOR = "#cdd6f4"
WORLD_PLATFORM_COLOR = "#a6adc8"

# Color Scheme - World List
WORLD_COUNT_COLOR = "#a6adc8"     # Color para contador de mundos
SELECTION_STATUS_COLOR = "#a6adc8"  # Color para estado de selección

# Color Scheme - Checkbox
CHECKBOX_BORDER_COLOR = "#7f849c"
CHECKBOX_CHECKED_BG_COLOR = "#74c7ec"
CHECKBOX_CHECKED_BORDER_COLOR = "#89dceb"

# Color Scheme - Facts Frame
FACTS_FRAME_BG_COLOR = "#1e1e21"  # Ligeramente más claro que el fondo principal


def get_main_window_style():
    """Devuelve el estilo para la ventana principal."""
    return f"""
        QWidget#mainBackground {{
            background-color: {BACKGROUND_COLOR};
        }}

        QMainWindow, QWidget {{
            background-color: transparent;
            color: {TEXT_COLOR};
        }}
    """


def get_button_style():
    """Devuelve el estilo para botones."""
    return f"""
        QPushButton {{
            background-color: {BUTTON_BG_COLOR};
            color: {BUTTON_TEXT_COLOR};
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 5px;
        }}
        QPushButton:hover {{
            background-color: {BUTTON_HOVER_COLOR};
        }}
        QPushButton:pressed {{
            background-color: {BUTTON_PRESSED_COLOR};
        }}
        QPushButton:disabled {{
            background-color: {BUTTON_DISABLED_BG_COLOR};
            color: {BUTTON_DISABLED_TEXT_COLOR};
        }}
    """


def get_tab_style():
    """Devuelve el estilo para pestañas."""
    return f"""
        QTabWidget::pane {{
            border: none;
            background: transparent;
        }}
        QTabBar::tab {{
            background-color: {TAB_BG_COLOR};
            color: {TAB_TEXT_COLOR};
            padding: 10px 20px;
            margin-right: 5px;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}
        QTabBar::tab:selected {{
            background-color: {TAB_SELECTED_BG_COLOR};
            color: {TAB_SELECTED_TEXT_COLOR};
            font-weight: bold;
        }}
    """


def get_progress_bar_style(success=False):
    """
    Devuelve el estilo para barras de progreso.

    Args:
        success: Si es True, usa el color de éxito para la barra
    """
    chunk_color = PROGRESS_BAR_SUCCESS_COLOR if success else PROGRESS_BAR_INFO_COLOR

    return f"""
        QProgressBar {{
            border: none;
            border-radius: 4px;
            background-color: {PROGRESS_BAR_BG_COLOR};
            text-align: center;
            color: white;
            height: 25px;
            font-weight: bold;
        }}
        QProgressBar::chunk {{
            background-color: {chunk_color};
            border-radius: 4px;
        }}
    """


def get_label_style():
    """Devuelve el estilo para etiquetas."""
    return f"""
        QLabel {{
            color: {TEXT_COLOR};
            background: transparent;
        }}
    """


def get_title_label_style():
    """Devuelve el estilo para etiquetas de título."""
    return f"""
        QLabel {{
            font-size: 22px;
            font-weight: bold; 
            color: {TITLE_COLOR};
        }}
    """


def get_checkbox_style():
    """Devuelve el estilo para checkboxes."""
    return f"""
        QCheckBox {{
            color: {TEXT_COLOR};
            background: transparent;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        QCheckBox::indicator:unchecked {{
            background-color: transparent;
            border: 2px solid {CHECKBOX_BORDER_COLOR};
            border-radius: 4px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {CHECKBOX_CHECKED_BG_COLOR};
            border: 2px solid {CHECKBOX_CHECKED_BORDER_COLOR};
            border-radius: 4px;
        }}
    """


def get_scrollbar_style():
    """Devuelve el estilo para barras de desplazamiento."""
    return f"""
        QScrollBar:vertical {{
            border: none;
            background-color: #313244;
            width: 10px;
            margin: 0px;
        }}
        QScrollBar::handle:vertical {{
            background-color: #585b70;
            min-height: 20px;
            border-radius: 5px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: none;
        }}
    """


def get_world_item_style():
    """Devuelve el estilo para elementos de mundo."""
    return f"""
        #worldItem {{
            overflow: hidden;
            background-color: transparent;
            border: 1px solid {WORLD_ITEM_BORDER_COLOR};
            border-radius: 8px;
            margin: 2px;
            padding: 0px;
        }}
        #worldItem:hover {{
            border-color: {WORLD_ITEM_HOVER_BORDER_COLOR};
            background-color: {WORLD_ITEM_HOVER_BG_COLOR};
            cursor: pointer;
        }}
    """


def get_world_icon_container_style():
    """Devuelve el estilo para el contenedor de icono de mundo."""
    return f"""
        #iconContainer {{
            overflow: hidden;
            border-top-left-radius: 7px;
            border-bottom-left-radius: 7px;
            padding: 0px;
            margin: 0px;
        }}
    """


def get_world_icon_label_style():
    """Devuelve el estilo para la etiqueta de icono de mundo."""
    return f"""
        #iconLabel {{
            background-color: {WORLD_ITEM_ICON_BG_COLOR};
            border-top-left-radius: 7px;
            border-bottom-left-radius: 7px;
            padding: 0px;
            margin: 0px;
            z-index: -1;
        }}
    """


def get_world_icon_mask_style():
    """Devuelve el estilo para la máscara de icono de mundo."""
    return f"""
        #iconMask {{
            border-top-left-radius: 7px;
            border-bottom-left-radius: 7px;
            padding: 0px;
            margin: 0px;
        }}
    """


def get_world_content_container_style():
    """Devuelve el estilo para el contenedor de contenido de mundo."""
    return f"""
        #contentContainer {{
            background-color: transparent;
            padding: 0px;
            margin: 0px;
        }}
    """


def get_world_name_label_style():
    """Devuelve el estilo para la etiqueta de nombre de mundo."""
    return f"""
        color: {WORLD_NAME_COLOR};
        font-weight: bold;
        font-size: 14px;
        background: transparent;
    """


def get_world_path_label_style():
    """Devuelve el estilo para la etiqueta de ruta de mundo."""
    return f"""
        color: {WORLD_PATH_COLOR};
        font-size: 11px;
        background: transparent;
    """


def get_world_platform_label_style():
    """Devuelve el estilo para la etiqueta de plataforma de mundo."""
    return f"""
        color: {WORLD_PLATFORM_COLOR};
        font-size: 11px;
        background: transparent;
    """


def get_world_checkbox_style():
    """Devuelve el estilo para el checkbox de selección de mundo."""
    return f"""
        QCheckBox {{
            margin-right: 5px;
        }}
        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
        }}
        QCheckBox::indicator:unchecked {{
            background-color: transparent;
            border: 2px solid {CHECKBOX_BORDER_COLOR};
            border-radius: 4px;
        }}
        QCheckBox::indicator:checked {{
            background-color: {CHECKBOX_CHECKED_BG_COLOR};
            border: 2px solid {CHECKBOX_CHECKED_BORDER_COLOR};
            border-radius: 4px;
        }}
    """


# Funciones para WorldListWidget

def get_world_count_label_style():
    """Devuelve el estilo para la etiqueta de conteo de mundos."""
    return f"""
        color: {WORLD_COUNT_COLOR};
    """


def get_selection_status_style():
    """Devuelve el estilo para la etiqueta de estado de selección."""
    return f"""
        color: {SELECTION_STATUS_COLOR};
        font-size: 12px;
    """


def get_worlds_widget_style():
    """Devuelve el estilo para el widget contenedor de mundos."""
    return f"""
        background: transparent;
    """


def get_world_list_scroll_area_style():
    """Devuelve el estilo completo para el área de desplazamiento de la lista de mundos."""
    return f"""
        QScrollArea {{
            border: none;
            background-color: transparent;
        }}
        {get_scrollbar_style()}
    """


def get_dialog_style():
    """Devuelve el estilo para diálogos."""
    return f"""
        QDialog {{
            background-color: {BACKGROUND_COLOR};
        }}
        {get_label_style()}
        {get_button_style()}
    """


def get_message_box_style():
    """Devuelve el estilo para cuadros de mensaje."""
    return f"""
        QMessageBox {{
            background-color: {BACKGROUND_COLOR};
        }}
        QLabel {{
            color: {TEXT_COLOR};
        }}
        {get_button_style()}
    """


def get_backup_progress_dialog_style():
    """Devuelve el estilo para el diálogo de progreso de respaldo."""
    return f"""
        QDialog {{
            background-color: {BACKGROUND_COLOR};
        }}
        QLabel {{
            color: {TEXT_COLOR};
            background: transparent;
        }}
        QFrame {{
            background-color: #1e1e21;
            border-radius: 8px;
            padding: 10px;
        }}
        {get_button_style()}
    """


def get_empty_state_style():
    """Devuelve el estilo para el widget de estado vacío."""
    return f"""
        QLabel[role="title"] {{
            font-size: 20px; 
            font-weight: bold; 
            color: #74c7ec;
        }}
        QLabel[role="message"] {{
            font-size: 14px;
            color: #cdd6f4;
        }}
        QLabel[role="reason"] {{
            font-size: 13px;
            color: #bac2de;
        }}
        QLabel[role="solution"] {{
            font-size: 14px;
            color: #cdd6f4;
            margin-top: 10px;
        }}
    """


# Nuevas funciones para BackupProgressDialog

def get_operation_title_style():
    """Devuelve el estilo para el título de operación en el diálogo de progreso."""
    return f"""
        font-size: 22px;
        font-weight: bold;
        color: #D4D4D8;
    """


def get_facts_frame_style():
    """Devuelve el estilo para el marco de curiosidades."""
    return f"""
        QFrame {{
            background-color: {FACTS_FRAME_BG_COLOR};
            border-radius: 8px;
            padding: 10px;
        }}
    """


def get_fact_title_style():
    """Devuelve el estilo para el título de las curiosidades."""
    return f"""
        font-size: 16px;
        font-weight: bold;
        color: #D4D4D8;
    """


def get_fact_content_style():
    """Devuelve el estilo para el contenido de las curiosidades."""
    return f"""
        font-size: 14px;
        padding: 10px;
        color: {TEXT_COLOR};
        background: transparent;
    """


def get_fact_counter_style():
    """Devuelve el estilo para el contador de curiosidades."""
    return f"""
        font-size: 12px;
        color: {TEXT_COLOR};
        background: transparent;
    """


def get_success_status_style():
    """Devuelve el estilo para el mensaje de estado cuando la operación es exitosa."""
    return f"""
        color: #D4D4D8;
        font-weight: bold;
        font-size: 16px;
    """


def load_stylesheet():
    """
    Carga la hoja de estilos para la aplicación.

    Si existe un archivo de estilos personalizado en resources/styles/dark_theme.qss,
    lo carga. De lo contrario, devuelve los estilos predeterminados combinados.

    Returns:
        str: Hoja de estilos para la aplicación
    """
    custom_style_path = "resources/styles/dark_theme.qss"

    if os.path.exists(custom_style_path):
        try:
            with open(custom_style_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error al cargar estilos personalizados: {e}")

    # Componer estilos a partir de funciones individuales
    return f"""
        {get_main_window_style()}
        {get_button_style()}
        {get_tab_style()}
        
        QFrame {{
            border: none;
        }}
        
        {get_label_style()}
        
        QScrollArea {{
            border: none;
            background: {BACKGROUND_COLOR};
        }}
        
        {get_progress_bar_style()}
        {get_checkbox_style()}
        {get_scrollbar_style()}
    """