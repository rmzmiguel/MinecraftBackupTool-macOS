"""
Base del sistema de proveedores para la detección de mundos de Minecraft.
Define la interfaz que deben implementar todos los proveedores de mundos.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class WorldProvider(ABC):
    """Clase base abstracta para todos los proveedores de mundos."""

    @property
    @abstractmethod
    def platform_name(self) -> str:
        """
        Nombre de la plataforma que este proveedor maneja.

        Returns:
            str: Nombre de la plataforma (ej. "Java", "Bedrock")
        """
        pass

    @abstractmethod
    def get_worlds(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de todos los mundos disponibles para esta plataforma.

        Returns:
            List[Dict[str, Any]]: Lista de diccionarios con datos de cada mundo,
                                 cada uno contiene al menos 'path', 'name', 'platform' e 'icon'
        """
        pass

    def is_available(self) -> bool:
        """
        Verifica si esta plataforma está disponible en el sistema actual.

        Puede usarse para deshabilitar proveedores que no son relevantes
        en el sistema operativo actual.

        Returns:
            bool: True si la plataforma está disponible, False en caso contrario
        """
        return True