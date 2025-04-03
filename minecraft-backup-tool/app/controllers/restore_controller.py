"""
Controlador para las operaciones de restauración de mundos.
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
from typing import Dict, List, Any, Callable, Optional
from PyQt6.QtCore import QThread, pyqtSignal

from app.providers.java_provider import JavaWorldProvider
from app.providers.bedrock_provider import BedrockWorldProvider


class RestoreOperation(QThread):
    """
    Hilo dedicado a realizar operaciones de restauración de mundos.
    """
    
    # Señales para comunicación con la UI
    progress_update = pyqtSignal(int, str)  # porcentaje, mensaje
    finished = pyqtSignal(bool, str)  # éxito, mensaje
    
    def __init__(self, source_zip: str):
        """
        Inicializa la operación de restauración.
        
        Args:
            source_zip: Ruta al archivo ZIP de respaldo
        """
        super().__init__()
        self.source_zip = source_zip
    
    def run(self):
        """Ejecuta la operación de restauración en segundo plano."""
        try:
            self._restore_worlds()
            self.finished.emit(True, "¡Restauración completada correctamente!")
        except Exception as e:
            self.finished.emit(False, f"Error durante la restauración: {str(e)}")
    
    def _restore_worlds(self):
        """Restaura los mundos desde un archivo ZIP."""
        if not self.source_zip or not os.path.exists(self.source_zip):
            self.finished.emit(False, "Archivo de respaldo inválido o no encontrado.")
            return
        
        # Crear carpeta temporal para extracción
        temp_dir = os.path.join(os.path.dirname(self.source_zip), "temp_restore")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Extraer archivo ZIP
            self.progress_update.emit(10, "Extrayendo archivo de respaldo...")
            with zipfile.ZipFile(self.source_zip, 'r') as zipf:
                zipf.extractall(temp_dir)
            
            # Obtener rutas para Java y Bedrock
            java_destination = JavaWorldProvider()._get_possible_locations()[0]
            bedrock_destination = BedrockWorldProvider()._get_possible_locations()[0]
            
            # Preparar para restauración
            worlds_to_restore = []
            
            # Buscar mundos de Java
            java_worlds_path = os.path.join(temp_dir, "Java")
            if os.path.exists(java_worlds_path):
                for world_folder in os.listdir(java_worlds_path):
                    world_path = os.path.join(java_worlds_path, world_folder)
                    if os.path.isdir(world_path):
                        worlds_to_restore.append((world_path, java_destination, "Java"))
            
            # Buscar mundos de Bedrock
            bedrock_worlds_path = os.path.join(temp_dir, "Bedrock")
            if os.path.exists(bedrock_worlds_path):
                for world_folder in os.listdir(bedrock_worlds_path):
                    world_path = os.path.join(bedrock_worlds_path, world_folder)
                    if os.path.isdir(world_path):
                        worlds_to_restore.append((world_path, bedrock_destination, "Bedrock"))
            
            # Verificar si hay mundos para restaurar
            if not worlds_to_restore:
                self.finished.emit(False, "No se encontraron mundos válidos en el respaldo.")
                return
            
            # Restaurar cada mundo
            total_worlds = len(worlds_to_restore)
            for i, (source_path, dest_base_path, platform) in enumerate(worlds_to_restore):
                world_name = os.path.basename(source_path)
                
                # Actualizar progreso
                progress = int(10 + (i / total_worlds) * 90)
                self.progress_update.emit(progress, f"Restaurando {world_name}...")
                
                # Leer metadatos si están disponibles
                metadata_path = os.path.join(source_path, "mc_backup_metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            if "name" in metadata:
                                world_name = metadata["name"]
                        # Eliminar el archivo de metadatos antes de copiar
                        os.remove(metadata_path)
                    except Exception:
                        # Si hay error, continuar con los datos existentes
                        pass
                
                # Determinar ruta de destino
                dest_path = os.path.join(dest_base_path, os.path.basename(source_path))
                
                # Si ya existe un mundo con el mismo nombre, crear una versión única
                if os.path.exists(dest_path):
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    dest_path = f"{dest_path}_{timestamp}"
                
                # Copiar el mundo a su destino
                shutil.copytree(source_path, dest_path)
            
            self.progress_update.emit(100, "¡Restauración completada!")
            
        finally:
            # Limpiar carpeta temporal
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


class RestoreController:
    """
    Controlador para gestionar operaciones de restauración de mundos.
    """
    
    def __init__(self):
        """Inicializa el controlador de restauración."""
        self.operation = None
    
    def restore_worlds(self, source_zip: str,
                      progress_callback: Callable[[int, str], None],
                      completion_callback: Callable[[bool, str], None]):
        """
        Inicia una operación de restauración de mundos.
        
        Args:
            source_zip: Ruta al archivo ZIP de respaldo
            progress_callback: Función para actualizar el progreso en la UI
            completion_callback: Función para manejar la finalización
        """
        # Crear y configurar la operación
        self.operation = RestoreOperation(source_zip)
        self.operation.progress_update.connect(progress_callback)
        self.operation.finished.connect(completion_callback)
        
        # Iniciar el proceso en segundo plano
        self.operation.start()
