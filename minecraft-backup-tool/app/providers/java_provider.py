"""
Proveedor de mundos para Minecraft Java Edition.
"""

import os
import logging
from typing import List, Dict, Any

from app.providers.base import WorldProvider
from app.models.world_registry import WorldRegistry

# Configurar logger
logger = logging.getLogger("JavaWorldProvider")

class JavaWorldProvider(WorldProvider):
    """Proveedor especializado en detectar mundos de Minecraft Java Edition."""

    @property
    def platform_name(self) -> str:
        """
        Returns:
            str: Nombre de la plataforma.
        """
        return "Java"

    def get_worlds(self) -> List[Dict[str, Any]]:
        """
        Busca mundos de Minecraft Java Edition en ubicaciones estándar y personalizadas.

        Returns:
            List[Dict[str, Any]]: Lista de mundos encontrados.
        """
        worlds = []
        location_count = 0

        # Buscar en todas las ubicaciones posibles
        for location in self._get_possible_locations():
            if os.path.exists(location):
                location_count += 1
                logger.info(f"Explorando directorio: {location}")

                try:
                    for world_folder in os.listdir(location):
                        world_path = os.path.join(location, world_folder)
                        if os.path.isdir(world_path):
                            # Verificar si es un mundo válido (tiene level.dat)
                            if os.path.exists(os.path.join(world_path, "level.dat")):
                                world_data = self._get_world_metadata(world_path, world_folder)
                                worlds.append(world_data)
                                logger.info(f"Mundo encontrado: {world_data['name']} en {world_path}")
                except PermissionError:
                    logger.warning(f"Sin permiso para acceder a: {location}")
                except Exception as e:
                    logger.error(f"Error al escanear {location}: {str(e)}")

        logger.info(f"Total de ubicaciones verificadas: {location_count}")
        logger.info(f"Total de mundos encontrados: {len(worlds)}")

        return worlds

    def _get_possible_locations(self) -> List[str]:
        """
        Obtiene todas las posibles ubicaciones donde pueden estar los mundos.

        Returns:
            List[str]: Lista de rutas a verificar.
        """
        locations = []

        # Ubicación estándar según el sistema operativo
        if os.name == 'nt':  # Windows
            # Minecraft estándar
            minecraft_dir = os.path.join(os.getenv('APPDATA', ''), '.minecraft')

            # Microsoft Store Edition
            ms_store_dir = os.path.join(
                os.getenv('LOCALAPPDATA', ''),
                'Packages',
                'Microsoft.4297127D64EC6_8wekyb3d8bbwe',
                'LocalState',
                'games',
                'com.mojang',
                '.minecraft'
            )

            if os.path.exists(ms_store_dir):
                locations.append(os.path.join(ms_store_dir, 'saves'))

        elif os.name == 'posix':  # Linux/Mac
            # Comprobar macOS primero
            mac_dirs = [
                os.path.expanduser('~/Library/Application Support/minecraft'),
                # Minecraft Launcher alternativo en Mac
                os.path.expanduser('~/Library/Application Support/minecraftlauncher')
            ]

            for mac_dir in mac_dirs:
                if os.path.exists(mac_dir):
                    locations.append(os.path.join(mac_dir, 'saves'))

            # Directorios Linux
            linux_dirs = [
                os.path.expanduser('~/.minecraft'),
                # Flatpak
                os.path.expanduser('~/.var/app/com.mojang.Minecraft/.minecraft'),
                # Snap
                os.path.expanduser('~/snap/minecraft/current/.minecraft'),
                # Steam Deck / Proton
                os.path.expanduser('~/.steam/steam/steamapps/compatdata/1745772215/pfx/drive_c/users/steamuser/AppData/Roaming/.minecraft')
            ]

            for linux_dir in linux_dirs:
                if os.path.exists(linux_dir):
                    locations.append(os.path.join(linux_dir, 'saves'))
        else:
            logger.warning(f"Sistema operativo no reconocido: {os.name}")
            minecraft_dir = None

        # Agregar .minecraft/saves si existe
        if 'minecraft_dir' in locals() and minecraft_dir and os.path.exists(minecraft_dir):
            locations.append(os.path.join(minecraft_dir, 'saves'))

        # Buscar instalaciones de MultiMC/PrismLauncher
        self._find_launcher_instances(locations)

        # Agregar ubicaciones personalizadas de la configuración
        custom_paths = WorldRegistry.get_config().get('custom_paths', {}).get('java', [])
        for custom_path in custom_paths:
            if os.path.exists(custom_path):
                locations.append(custom_path)
                logger.info(f"Agregando ruta personalizada: {custom_path}")

        # Eliminar duplicados preservando el orden
        unique_locations = []
        for location in locations:
            if location not in unique_locations:
                unique_locations.append(location)

        logger.info(f"Ubicaciones a verificar: {len(unique_locations)}")
        return unique_locations

    def _find_launcher_instances(self, locations: List[str]) -> None:
        """
        Busca instancias de Minecraft en launchers alternativos como MultiMC, PrismLauncher, ATLauncher.

        Args:
            locations: Lista donde agregar las ubicaciones encontradas
        """
        if os.name == 'nt':  # Windows
            launcher_dirs = [
                # MultiMC
                os.path.join(os.environ.get('APPDATA', ''), 'MultiMC'),
                # PrismLauncher
                os.path.join(os.environ.get('APPDATA', ''), 'PrismLauncher'),
                # ATLauncher
                os.path.join(os.environ.get('APPDATA', ''), 'ATLauncher', 'instances')
            ]
        elif os.name == 'posix':  # Linux/Mac
            launcher_dirs = [
                # MultiMC (Mac)
                os.path.expanduser('~/Library/Application Support/MultiMC'),
                # PrismLauncher (Mac)
                os.path.expanduser('~/Library/Application Support/PrismLauncher'),
                # MultiMC (Linux)
                os.path.expanduser('~/.local/share/multimc'),
                os.path.expanduser('~/MultiMC'),
                # PrismLauncher (Linux)
                os.path.expanduser('~/.local/share/PrismLauncher'),
                os.path.expanduser('~/PrismLauncher'),
                # ATLauncher
                os.path.expanduser('~/.local/share/atlauncher/instances'),
                os.path.expanduser('~/Library/Application Support/ATLauncher/instances')
            ]
        else:
            return

        for launcher_dir in launcher_dirs:
            if os.path.exists(launcher_dir):
                logger.info(f"Launcher encontrado: {launcher_dir}")

                # Para ATLauncher, las instancias están directamente en el directorio
                if "ATLauncher" in launcher_dir and "instances" in launcher_dir:
                    for instance in os.listdir(launcher_dir):
                        instance_dir = os.path.join(launcher_dir, instance, '.minecraft', 'saves')
                        if os.path.exists(instance_dir):
                            locations.append(instance_dir)
                            logger.info(f"Instancia ATLauncher encontrada: {instance_dir}")
                else:
                    # Para MultiMC/PrismLauncher
                    instances_dir = os.path.join(launcher_dir, 'instances')
                    if os.path.exists(instances_dir):
                        for instance in os.listdir(instances_dir):
                            # Comprobar el archivo instance.cfg para confirmar que es una instancia
                            instance_path = os.path.join(instances_dir, instance)
                            if os.path.isdir(instance_path) and os.path.exists(os.path.join(instance_path, 'instance.cfg')):
                                minecraft_dir = os.path.join(instance_path, '.minecraft')
                                # Algunos packs usan "minecraft" en lugar de ".minecraft"
                                if not os.path.exists(minecraft_dir):
                                    minecraft_dir = os.path.join(instance_path, 'minecraft')

                                saves_dir = os.path.join(minecraft_dir, 'saves')
                                if os.path.exists(saves_dir):
                                    locations.append(saves_dir)
                                    logger.info(f"Instancia MultiMC/Prism encontrada: {saves_dir}")

    def _get_world_metadata(self, world_path: str, default_name: str) -> Dict[str, Any]:
        """
        Extrae metadatos del mundo.

        Args:
            world_path: Ruta a la carpeta del mundo.
            default_name: Nombre por defecto (nombre de la carpeta).

        Returns:
            Dict[str, Any]: Metadatos del mundo.
        """
        # Intentar leer level.dat para extraer el nombre real del mundo
        # En una implementación completa, aquí se usaría la biblioteca NBT
        # Por simplicidad, usamos el nombre de la carpeta
        name = default_name

        # Verificar si hay un ícono
        icon_path = os.path.join(world_path, "icon.png")
        if not os.path.exists(icon_path):
            icon_path = None

        return {
            'path': world_path,
            'name': name,
            'platform': self.platform_name,
            'icon': icon_path
        }