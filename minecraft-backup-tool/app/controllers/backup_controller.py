"""
Controlador para las operaciones de respaldo de mundos.
"""

import os
import json
import shutil
import zipfile
from datetime import datetime
from typing import List, Tuple, Dict, Any, Callable
from PyQt6.QtCore import QThread, pyqtSignal


class BackupOperation(QThread):
    """
    Hilo dedicado a realizar operaciones de respaldo de mundos.
    """
    
    # Señales para comunicación con la UI
    progress_update = pyqtSignal(int, str)  # porcentaje, mensaje
    finished = pyqtSignal(bool, str)  # éxito, mensaje
    
    def __init__(self, worlds: List[Tuple[str, str, str]], destination: str):
        """
        Inicializa la operación de respaldo.
        
        Args:
            worlds: Lista de tuplas (ruta, plataforma, nombre) de mundos a respaldar
            destination: Carpeta de destino para el archivo ZIP de respaldo
        """
        super().__init__()
        self.worlds = worlds
        self.destination = destination
    
    def run(self):
        """Ejecuta la operación de respaldo en segundo plano."""
        try:
            self._backup_worlds()
            self.finished.emit(True, "¡Respaldo completado correctamente!")
        except Exception as e:
            self.finished.emit(False, f"Error durante el respaldo: {str(e)}")
    
    def _backup_worlds(self):
        """Realiza el respaldo de los mundos a un archivo ZIP."""
        total_worlds = len(self.worlds)
        if total_worlds == 0:
            self.finished.emit(False, "No hay mundos seleccionados para respaldar.")
            return
        
        # Crear nombre de archivo con marca de tiempo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"minecraft_worlds_backup_{timestamp}.zip"
        zip_path = os.path.join(self.destination, zip_filename)
        
        # Crear carpeta temporal para organizar mundos por plataforma
        temp_dir = os.path.join(os.path.dirname(zip_path), "temp_backup")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Procesar cada mundo
            for i, (world_path, platform, world_name) in enumerate(self.worlds):
                # Actualizar progreso
                progress = int((i / total_worlds) * 90)  # Reservar 10% para la compresión
                self.progress_update.emit(progress, f"Respaldando {world_name}...")
                
                # Crear directorio de plataforma en la carpeta temporal
                platform_dir = os.path.join(temp_dir, platform)
                os.makedirs(platform_dir, exist_ok=True)
                
                # Copiar carpeta del mundo a la estructura temporal
                world_temp_path = os.path.join(platform_dir, os.path.basename(world_path))
                shutil.copytree(world_path, world_temp_path)
                
                # Añadir metadatos para facilitar la restauración
                with open(os.path.join(world_temp_path, "mc_backup_metadata.json"), 'w', encoding='utf-8') as f:
                    json.dump({
                        "name": world_name,
                        "platform": platform,
                        "original_path": world_path,
                        "backup_date": datetime.now().isoformat()
                    }, f, ensure_ascii=False, indent=2)
            
            # Comprimir la estructura temporal en un ZIP
            self.progress_update.emit(90, "Creando archivo ZIP...")
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            self.progress_update.emit(100, "¡Respaldo completado!")
            
        finally:
            # Limpiar carpeta temporal
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


class BackupController:
    """
    Controlador para gestionar operaciones de respaldo de mundos.
    """
    
    def __init__(self):
        """Inicializa el controlador de respaldo."""
        self.operation = None
    
    def backup_worlds(self, worlds: List[Tuple[str, str, str]], destination: str,
                     progress_callback: Callable[[int, str], None], 
                     completion_callback: Callable[[bool, str], None]):
        """
        Inicia una operación de respaldo de mundos.
        
        Args:
            worlds: Lista de tuplas (ruta, plataforma, nombre) de mundos a respaldar
            destination: Carpeta de destino para el archivo ZIP
            progress_callback: Función para actualizar el progreso en la UI
            completion_callback: Función para manejar la finalización
        """
        # Crear y configurar la operación
        self.operation = BackupOperation(worlds, destination)
        self.operation.progress_update.connect(progress_callback)
        self.operation.finished.connect(completion_callback)
        
        # Iniciar el proceso en segundo plano
        self.operation.start()
