"""
Utilidades para internacionalización de la aplicación.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Configurar logger
logger = logging.getLogger("I18n")

# Idioma predeterminado
DEFAULT_LANGUAGE = "es"

# Diccionario global para almacenar las traducciones
translations = {}


def load_translations(language: str = DEFAULT_LANGUAGE) -> bool:
    """
    Carga el archivo de traducciones para el idioma especificado.

    Args:
        language: Código de idioma (ej. "es", "en")

    Returns:
        bool: True si se cargó correctamente, False en caso contrario
    """
    global translations

    # Ruta al archivo de traducciones
    trans_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "resources",
        "translations",
        f"{language}.json"
    )

    # Verificar si existe el archivo
    if not os.path.exists(trans_path):
        logger.warning(f"Archivo de traducciones no encontrado: {trans_path}")

        # Si no es el idioma predeterminado, intentar cargar el predeterminado
        if language != DEFAULT_LANGUAGE:
            logger.info(f"Intentando cargar el idioma predeterminado: {DEFAULT_LANGUAGE}")
            return load_translations(DEFAULT_LANGUAGE)

        return False

    # Cargar traducciones
    try:
        with open(trans_path, 'r', encoding='utf-8') as f:
            translations = json.load(f)

        logger.info(f"Traducciones cargadas para {language}")
        return True
    except Exception as e:
        logger.error(f"Error al cargar traducciones: {e}")

        # Si no es el idioma predeterminado, intentar cargar el predeterminado
        if language != DEFAULT_LANGUAGE:
            logger.info(f"Intentando cargar el idioma predeterminado: {DEFAULT_LANGUAGE}")
            return load_translations(DEFAULT_LANGUAGE)

        return False


def get_text(key: str, default: Optional[str] = None) -> str:
    """
    Obtiene el texto traducido para la clave especificada.

    Args:
        key: Clave del texto a traducir
        default: Texto predeterminado si no se encuentra la clave

    Returns:
        str: Texto traducido o el valor predeterminado
    """
    # Si las traducciones no están cargadas, intentar cargar
    if not translations:
        load_translations()

    # Buscar la clave en las traducciones
    result = translations.get(key)

    # Si no se encuentra y hay un valor predeterminado, usarlo
    if result is None and default is not None:
        return default

    # Si no se encuentra y no hay valor predeterminado, usar la clave
    if result is None:
        logger.warning(f"Clave de traducción no encontrada: {key}")
        return key

    return result


def initialize(language: Optional[str] = None) -> None:
    """
    Inicializa el sistema de traducciones.

    Args:
        language: Código de idioma a cargar, o None para usar el predeterminado
    """
    # Crear directorio de traducciones si no existe
    trans_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "resources",
        "translations"
    )
    os.makedirs(trans_dir, exist_ok=True)

    # Crear archivo de ejemplo si no existe ningún archivo de traducción
    example_path = os.path.join(trans_dir, f"{DEFAULT_LANGUAGE}.json")
    if not os.listdir(trans_dir):
        example_translations = {
            "app.name": "Minecraft Backup Tool",
            "button.backup": "Respaldar mundos seleccionados",
            "button.restore": "Restaurar mundos",
            "button.close": "Cerrar",
            "button.about": "Acerca de",
            "label.ready": "Listo para respaldar o restaurar mundos de Minecraft",
            "dialog.backup.title": "Progreso de respaldo",
            "dialog.restore.title": "Progreso de restauración",
            "dialog.about.title": "Acerca de Minecraft Backup Tool",
            "dialog.select_destination": "Seleccionar destino del respaldo",
            "dialog.select_backup": "Seleccionar archivo de respaldo",
            "message.no_selection": "Por favor, selecciona al menos un mundo para respaldar.",
            "message.backup_complete": "¡Respaldo completado correctamente!",
            "message.restore_complete": "¡Restauración completada correctamente!",
            "message.no_worlds": "No se encontraron mundos de Minecraft",
            "message.select_all": "Seleccionar todo",
            "empty.title": "No se encontraron mundos de Minecraft",
            "empty.message": "No se han detectado mundos de Minecraft en las ubicaciones habituales.",
            "empty.reason1": "Minecraft no está instalado en este equipo",
            "empty.reason2": "Aún no has creado ningún mundo en Minecraft",
            "empty.reason3": "Minecraft está instalado en una ubicación no estándar",
            "empty.reason4": "Los permisos de acceso a la carpeta de Minecraft son insuficientes",
            "empty.solution": "Puedes restaurar mundos desde un respaldo existente o verificar la configuración para añadir ubicaciones personalizadas donde buscar mundos."
        }

        try:
            with open(example_path, 'w', encoding='utf-8') as f:
                json.dump(example_translations, f, ensure_ascii=False, indent=2)
            logger.info(f"Archivo de traducciones de ejemplo creado en {example_path}")
        except Exception as e:
            logger.error(f"Error al crear archivo de traducciones de ejemplo: {e}")

    # Cargar traducciones
    load_translations(language or DEFAULT_LANGUAGE)