"""
Punto de entrada principal para la aplicación Minecraft Backup Tool.

Este módulo maneja la inicialización de la aplicación PyQt6, incluyendo:
- Configuración de fuentes personalizadas
- Configuración de logging e internacionalización
- Mostrar una pantalla de inicio atractiva
- Cargar y mostrar la ventana principal
"""

import sys
import os
import logging
from PyQt6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from PyQt6.QtGui import QPixmap, QFont, QFontDatabase, QColor, QPainter, QImage
from PyQt6.QtCore import Qt, QTimer, QSize

# Inicializar sistemas básicos antes de importar otros módulos
from app.utils.logging import setup_logging, get_logger
from app.utils.config import get_config
from app.utils.i18n import initialize as init_i18n, get_text

# Configurar logging
setup_logging()
logger = get_logger("MinecraftBackupTool")

# Importar después de inicializar sistemas básicos
from app.views.main_window import MainWindow


def setup_application_font(app):
    """
    Configura la fuente personalizada para toda la aplicación.

    Args:
        app: Instancia de QApplication

    Returns:
        bool: True si se aplicó correctamente la fuente, False en caso contrario
    """
    # Ruta a la carpeta de fuentes
    font_path = os.path.join(os.path.dirname(__file__), "resources", "fonts",
                             "InstrumentSans-VariableFont_wdth,wght.ttf")

    # Verificar si el archivo existe
    if os.path.exists(font_path):
        # Cargar la fuente desde el archivo
        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id != -1:
            # Obtener el nombre de la familia de fuentes
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                # Crear la fuente y aplicarla a la aplicación
                custom_font = QFont(font_families[0], 10)
                app.setFont(custom_font)
                logger.info(f"Fuente aplicada: {font_families[0]}")
                return True

    logger.warning(f"No se pudo cargar la fuente desde: {font_path}")
    return False


def create_splash_screen():
    """
    Crea y configura una pantalla de inicio atractiva.

    Returns:
        QSplashScreen: Objeto de pantalla de inicio configurado
    """
    # Verificar si debe mostrarse la pantalla de inicio
    if not get_config().get("appearance.show_splash", True):
        return None

    # Verificar si existe una imagen personalizada
    splash_path = os.path.join(os.path.dirname(__file__), "resources", "icons", "splash.png")

    if os.path.exists(splash_path):
        logger.info("Usando imagen de splash personalizada")
        splash_pixmap = QPixmap(splash_path)
    else:
        # Crear una imagen atractiva para el splash screen
        logger.info("Creando imagen de splash predeterminada")
        splash_size = QSize(600, 350)
        img = QImage(splash_size, QImage.Format.Format_ARGB32)
        img.fill(QColor("#18181B"))  # Fondo oscuro

        # Configurar el pintor para dibujar en la imagen
        painter = QPainter(img)

        # Intentar usar una fuente personalizada para el título
        font_id = QFontDatabase.addApplicationFont(os.path.join(
            os.path.dirname(__file__),
            "resources", "fonts", "InstrumentSans-VariableFont_wdth,wght.ttf"
        ))

        if font_id != -1:
            font_families = QFontDatabase.applicationFontFamilies(font_id)
            if font_families:
                painter.setFont(QFont(font_families[0], 24, QFont.Weight.Bold))
            else:
                painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        else:
            painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))

        # Dibujar un gradiente o un fondo más interesante si lo deseas
        # (aquí podrías añadir más elementos gráficos)

        # Dibujar el título
        painter.setPen(QColor(209, 213, 219))  # Color gris claro
        painter.drawText(img.rect(),
                         Qt.AlignmentFlag.AlignCenter,
                         get_text("app.name", "Minecraft Backup Tool"))

        # Dibujar el subtítulo
        painter.setFont(QFont(painter.font().family(), 12))
        painter.setPen(QColor(156, 163, 175))  # Color gris más claro
        subtitle_rect = img.rect()
        subtitle_rect.setTop(img.rect().center().y() + 20)
        painter.drawText(subtitle_rect,
                         Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                         "By Miguel Ramírez")

        # Finalizar la pintura
        painter.end()

        # Convertir la imagen a pixmap
        splash_pixmap = QPixmap.fromImage(img)

        # Guardar la imagen para futuros usos
        os.makedirs(os.path.dirname(splash_path), exist_ok=True)
        splash_pixmap.save(splash_path)

    # Crear la pantalla de splash con el pixmap
    splash = QSplashScreen(splash_pixmap)

    # Configurar mensaje si se desea
    splash.showMessage(get_text("splash.initializing", "Inicializando aplicación..."),
                       Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                       Qt.GlobalColor.white)

    return splash


def setup_update_check():
    """Configura la verificación de actualizaciones."""
    # Importar después para evitar dependencias circulares
    from app.utils.update import check_for_updates

    # Verificar si está habilitada la verificación automática
    if get_config().get("updates.check_updates", True):
        def handle_update_available(version, url, changelog):
            """Manejador para cuando hay una actualización disponible."""
            message = (
                f"<h3>¡Nueva versión disponible!</h3>"
                f"<p>Está disponible la versión {version} de Minecraft Backup Tool.</p>"
                f"<p><b>Cambios en esta versión:</b></p>"
                f"<div style='background-color: #1e1e21; padding: 10px; "
                f"border-radius: 5px; max-height: 200px; overflow-y: auto;'>"
                f"{changelog}</div>"
                f"<p>¿Deseas descargar la nueva versión?</p>"
            )

            dialog = QMessageBox()
            dialog.setWindowTitle("Actualización disponible")
            dialog.setTextFormat(Qt.TextFormat.RichText)
            dialog.setText(message)
            dialog.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            # Aplicar estilos
            from app.utils.styles import get_message_box_style
            dialog.setStyleSheet(get_message_box_style())

            # Si el usuario acepta, abrir página de descarga
            if dialog.exec() == QMessageBox.StandardButton.Yes:
                from app.utils.update import open_download_page
                open_download_page(url)

        # Programar verificación (retrasar 5 segundos para que la aplicación cargue primero)
        logger.info("Verificación de actualizaciones programada")
        QTimer.singleShot(5000, lambda: check_for_updates(False, handle_update_available))


def initialize_resources():
    """Inicializa y verifica los recursos necesarios para la aplicación."""
    # Crear directorios necesarios
    resource_dirs = [
        "resources/icons",
        "resources/fonts",
        "resources/styles",
        "resources/translations"
    ]

    for directory in resource_dirs:
        os.makedirs(directory, exist_ok=True)
        logger.debug(f"Directorio de recursos verificado: {directory}")

    # Verificar archivo de estilos
    style_path = "resources/styles/dark_theme.qss"
    if not os.path.exists(style_path):
        logger.info(f"Archivo de estilos no encontrado: {style_path}")

        # Aquí podríamos crear un archivo de estilos predeterminado si lo deseamos

    logger.info("Recursos inicializados correctamente")


def main():
    """Función principal de entrada de la aplicación."""
    # Obtener el idioma configurado
    config = get_config()
    language = config.get("appearance.language", "es")

    # Inicializar internacionalización
    init_i18n(language)

    # Inicializar recursos
    if not getattr(sys, 'frozen', False):
        initialize_resources()

    # Registrar excepciones no capturadas
    sys.excepthook = lambda exctype, value, traceback: logger.critical(
        f"Excepción no capturada: {exctype.__name__}: {value}",
        exc_info=(exctype, value, traceback)
    )

    # Crear la aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Minecraft Backup Tool")
    app.setOrganizationName("MiguelRamirez")
    app.setOrganizationDomain("miguelramirez.dev")

    # Aplicar la fuente personalizada
    setup_application_font(app)

    # Mostrar la pantalla de inicio si está habilitada
    splash = create_splash_screen()
    if splash:
        splash.show()
        app.processEvents()  # Asegurar que la splash screen se muestre inmediatamente

    # Programar verificación de actualizaciones
    setup_update_check()

    # Crear la ventana principal (pero aún no mostrarla)
    window = MainWindow()

    # Función para cerrar la splash screen y mostrar la ventana principal
    def finish_splash():
        if splash:
            splash.finish(window)
        window.show()
        logger.info("Aplicación inicializada y lista")

    # Configurar el temporizador para cerrar la splash screen después de 2 segundos
    splash_time = 2000 if splash else 0
    QTimer.singleShot(splash_time, finish_splash)

    # Iniciar el bucle principal de eventos
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logger.critical(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)