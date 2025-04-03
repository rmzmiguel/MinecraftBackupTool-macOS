"""
Proveedor de mundos para Minecraft Bedrock Edition.
"""

import os
from typing import List, Dict, Any

from app.providers.base import WorldProvider
from app.models.world_registry import WorldRegistry


class BedrockWorldProvider(WorldProvider):
    """Proveedor especializado en detectar mundos de Minecraft Bedrock Edition."""
    
    @property
    def platform_name(self) -> str:
        """
        Returns:
            str: Nombre de la plataforma.
        """
        return "Bedrock"
    
    def get_worlds(self) -> List[Dict[str, Any]]:
        """
        Busca mundos de Minecraft Bedrock Edition en ubicaciones estándar y personalizadas.
        
        Returns:
            List[Dict[str, Any]]: Lista de mundos encontrados.
        """
        worlds = []
        
        # Buscar en todas las ubicaciones posibles
        for location in self._get_possible_locations():
            if os.path.exists(location):
                for world_folder in os.listdir(location):
                    world_path = os.path.join(location, world_folder)
                    if os.path.isdir(world_path):
                        # Verificar si es un mundo válido (tiene levelname.txt)
                        if os.path.exists(os.path.join(world_path, "levelname.txt")):
                            world_data = self._get_world_metadata(world_path, world_folder)
                            worlds.append(world_data)
        
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
            bedrock_dir = os.path.join(
                os.getenv('LOCALAPPDATA', ''),
                'Packages',
                'Microsoft.MinecraftUWP_8wekyb3d8bbwe',
                'LocalState',
                'games',
                'com.mojang'
            )
            if os.path.exists(bedrock_dir):
                locations.append(os.path.join(bedrock_dir, 'minecraftWorlds'))
        elif os.name == 'posix':  # Linux/Mac
            if os.path.exists(os.path.expanduser('~/Library/Application Support/com.mojang.minecraftpe')):
                # macOS
                bedrock_dir = os.path.expanduser(
                    '~/Library/Application Support/com.mojang.minecraftpe/games/com.mojang'
                )
                if os.path.exists(bedrock_dir):
                    locations.append(os.path.join(bedrock_dir, 'minecraftWorlds'))
            else:
                # Linux
                bedrock_dir = os.path.expanduser('~/.local/share/mcpelauncher/games/com.mojang')
                if os.path.exists(bedrock_dir):
                    locations.append(os.path.join(bedrock_dir, 'minecraftWorlds'))
        
        # Agregar ubicaciones personalizadas de la configuración
        custom_paths = WorldRegistry.get_config().get('custom_paths', {}).get('bedrock', [])
        for custom_path in custom_paths:
            if os.path.exists(custom_path):
                locations.append(custom_path)
        
        return locations
    
    def _get_world_metadata(self, world_path: str, default_name: str) -> Dict[str, Any]:
        """
        Extrae metadatos del mundo.
        
        Args:
            world_path: Ruta a la carpeta del mundo.
            default_name: Nombre por defecto (nombre de la carpeta).
            
        Returns:
            Dict[str, Any]: Metadatos del mundo.
        """
        # Intentar obtener el nombre real desde levelname.txt
        name = default_name
        levelname_txt = os.path.join(world_path, "levelname.txt")
        if os.path.exists(levelname_txt):
            try:
                with open(levelname_txt, 'r', encoding='utf-8') as f:
                    name = f.read().strip()
            except Exception:
                # Si hay error, usar el nombre por defecto
                pass
        
        # Verificar si hay un ícono
        icon_path = os.path.join(world_path, "world_icon.jpeg")
        if not os.path.exists(icon_path):
            icon_path = None
        
        return {
            'path': world_path,
            'name': name,
            'platform': self.platform_name,
            'icon': icon_path
        }
