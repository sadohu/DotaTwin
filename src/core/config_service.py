"""
Servicio de gestión de configuraciones para Dota 2 Config Copier.

Este módulo maneja la persistencia de configuraciones y operaciones
de copia de archivos siguiendo principios de responsabilidad única.
"""

import os
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from ..models.domain_models import AppConfig, CopyOperation, SteamAccount
from config.settings import CACHE_FILE, CONFIG_PATTERNS, EXCLUDE_FOLDERS

logger = logging.getLogger(__name__)

REMOTECACHE_FILE = "remotecache.vdf"


class ConfigurationService:
    """
    Servicio para gestionar configuraciones persistentes de la aplicación.
    
    Maneja la carga, guardado y migración de configuraciones de usuario.
    """
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Inicializa el servicio de configuración.
        
        Args:
            config_file: Ruta del archivo de configuración (opcional)
        """
        self.config_file = config_file or Path(CACHE_FILE)
        self._config: Optional[AppConfig] = None
    
    @property
    def config(self) -> AppConfig:
        """
        Obtiene la configuración actual, cargándola si es necesario.
        
        Returns:
            Configuración de la aplicación
        """
        if self._config is None:
            self._config = self.load_config()
        return self._config
    
    def load_config(self) -> AppConfig:
        """
        Carga la configuración desde el archivo.
        
        Returns:
            Configuración cargada o por defecto
        """
        try:
            config = AppConfig.load_from_file(self.config_file)
            self._config = config
            logger.info(f"Configuración cargada desde {self.config_file}")
            return config
            
        except Exception as e:
            logger.warning(f"Error cargando configuración: {e}")
            return AppConfig()
    
    def save_config(self, config: Optional[AppConfig] = None) -> bool:
        """
        Guarda la configuración al archivo.
        
        Args:
            config: Configuración a guardar (usa la actual si es None)
            
        Returns:
            True si se guardó correctamente
        """
        config_to_save = config or self.config
        
        try:
            success = config_to_save.save_to_file(self.config_file)
            if success:
                self._config = config_to_save
                logger.info(f"Configuración guardada en {self.config_file}")
            else:
                logger.error("Error guardando configuración")
            
            return success
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            return False
    
    def update_selection(self, origen: str, destino: str) -> bool:
        """
        Actualiza la selección de origen y destino.
        
        Args:
            origen: Steam ID de la cuenta origen
            destino: Steam ID de la cuenta destino
            
        Returns:
            True si se actualizó correctamente
        """
        self.config.update_selection(origen, destino)
        return self.save_config()
    
    def ignore_account(self, steamid: str) -> bool:
        """
        Agrega una cuenta a la lista de ignoradas.
        
        Args:
            steamid: Steam ID de la cuenta a ignorar
            
        Returns:
            True si se actualizó correctamente
        """
        self.config.add_ignored_account(steamid)
        return self.save_config()
    
    def restore_account(self, steamid: str) -> bool:
        """
        Remueve una cuenta de la lista de ignoradas.
        
        Args:
            steamid: Steam ID de la cuenta a restaurar
            
        Returns:
            True si se actualizó correctamente
        """
        self.config.remove_ignored_account(steamid)
        return self.save_config()
    
    def update_pagination_settings(self, items_per_page: int) -> bool:
        """
        Actualiza la configuración de paginación.
        
        Args:
            items_per_page: Número de elementos por página
            
        Returns:
            True si se actualizó correctamente
        """
        self.config.items_por_pagina = items_per_page
        return self.save_config()
    
    def update_window_geometry(self, geometry: str) -> bool:
        """
        Actualiza la geometría de la ventana.
        
        Args:
            geometry: String de geometría (ej: "800x600")
            
        Returns:
            True si se actualizó correctamente
        """
        self.config.window_geometry = geometry
        return self.save_config()
    
    def get_ignored_accounts(self) -> List[str]:
        """
        Obtiene la lista de cuentas ignoradas.
        
        Returns:
            Lista de Steam IDs ignorados
        """
        return self.config.cuentas_ignoradas.copy()
    
    def is_account_ignored(self, steamid: str) -> bool:
        """
        Verifica si una cuenta está ignorada.
        
        Args:
            steamid: Steam ID a verificar
            
        Returns:
            True si la cuenta está ignorada
        """
        return self.config.is_ignored(steamid)
    
    def reset_config(self) -> bool:
        """
        Resetea la configuración a valores por defecto.
        
        Returns:
            True si se reseteo correctamente
        """
        self._config = AppConfig()
        return self.save_config()


class FileCopyService:
    """
    Servicio para realizar operaciones de copia de archivos.
    
    Maneja la copia recursiva de configuraciones con validaciones
    y manejo de errores robusto.
    """
    
    def __init__(self, enable_backup: bool = True):
        """
        Inicializa el servicio de copia.
        
        Args:
            enable_backup: Habilita backups automáticos
        """
        self.enable_backup = enable_backup
    
    def copy_configuration(self, operation: CopyOperation) -> Tuple[bool, str]:
        """
        Copia la configuración entre cuentas.
        
        Args:
            operation: Operación de copia a realizar
            
        Returns:
            Tupla (éxito, mensaje)
        """
        if not operation.is_valid:
            return False, "Operación de copia inválida"
        
        try:
            # Crear backup si está habilitado
            if self.enable_backup and operation.backup_enabled:
                backup_success = self._create_backup(operation)
                if not backup_success:
                    logger.warning("No se pudo crear backup, continuando sin él")
            
            # Realizar la copia
            success = self._copy_folder_recursive(
                operation.origen.ruta, 
                operation.destino.ruta
            )
            
            if success:
                logger.info(f"Configuración copiada: {operation.description}")
                return True, "Configuración copiada exitosamente"
            else:
                return False, "Error durante la copia de archivos"
                
        except Exception as e:
            error_msg = f"Error inesperado durante la copia: {e}"
            logger.error(error_msg)
            return False, error_msg
    
    def _create_backup(self, operation: CopyOperation) -> bool:
        """
        Crea un backup de la configuración destino.
        
        Args:
            operation: Operación de copia
            
        Returns:
            True si se creó el backup correctamente
        """
        try:
            backup_path = operation.get_backup_path()
            
            if operation.destino.ruta.exists():
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(operation.destino.ruta, backup_path)
                logger.info(f"Backup creado en: {backup_path}")
                return True
            
            return True  # No hay nada que respaldar
            
        except (OSError, shutil.Error) as e:
            logger.error(f"Error creando backup: {e}")
            return False
    
    def _copy_folder_recursive(self, origen: Path, destino: Path) -> bool:
        """
        Copia una carpeta de forma recursiva (método simplificado v2.1.2).
        
        Args:
            origen: Carpeta origen
            destino: Carpeta destino
            
        Returns:
            True si la copia fue exitosa
        """
        try:
            # Asegurar que el directorio padre del destino existe
            # (crea userdata/<id> si la cuenta nunca abrió Dota 2)
            destino.parent.mkdir(parents=True, exist_ok=True)

            # remotecache.vdf es el estado de Steam Cloud de cada cuenta. Copiar el
            # del origen hace que Steam crea que los archivos ya están sincronizados
            # y los reemplace con la nube del destino, así que se conserva el propio.
            remotecache_destino = destino / REMOTECACHE_FILE
            remotecache_original = (remotecache_destino.read_bytes()
                                    if remotecache_destino.is_file() else None)

            # Eliminar destino si existe para hacer una copia limpia
            if destino.exists():
                shutil.rmtree(destino)

            # Copiar toda la carpeta recursivamente, menos el remotecache.vdf raíz
            def ignorar_remotecache(carpeta, nombres):
                return [REMOTECACHE_FILE] if Path(carpeta) == origen else []

            shutil.copytree(origen, destino, ignore=ignorar_remotecache)

            if remotecache_original is not None:
                remotecache_destino.write_bytes(remotecache_original)
            
            logger.info(f"Carpeta copiada completamente: {origen} -> {destino}")
            return True
            
        except (OSError, shutil.Error, PermissionError) as e:
            logger.error(f"Error copiando carpeta {origen} -> {destino}: {e}")
            return False
    
    def validate_paths(self, origen: Path, destino: Path) -> Tuple[bool, str]:
        """
        Valida que las rutas sean accesibles para la copia.
        
        Args:
            origen: Ruta origen
            destino: Ruta destino
            
        Returns:
            Tupla (válido, mensaje_error)
        """
        if not origen.exists():
            return False, f"La ruta origen no existe: {origen}"
        
        if not origen.is_dir():
            return False, f"La ruta origen no es un directorio: {origen}"
        
        try:
            # Verificar permisos de escritura en destino
            destino.parent.mkdir(parents=True, exist_ok=True)
            test_file = destino.parent / "test_write_permissions"
            test_file.touch()
            test_file.unlink()
            
        except (OSError, PermissionError):
            return False, f"Sin permisos de escritura en: {destino.parent}"
        
        return True, ""
    
    def get_copy_size_estimate(self, origen: Path) -> int:
        """
        Estima el tamaño de la copia en bytes.
        
        Args:
            origen: Carpeta origen
            
        Returns:
            Tamaño estimado en bytes
        """
        total_size = 0
        
        try:
            # Calcular tamaño de toda la carpeta (simplificado)
            for root, dirs, files in os.walk(origen):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        total_size += file_path.stat().st_size
                    except (OSError, FileNotFoundError):
                        continue
                        
        except (OSError, PermissionError):
            logger.warning(f"No se pudo calcular el tamaño de {origen}")
        
        return total_size
    
    def cleanup_old_backups(self, max_backups: int = 10) -> None:
        """
        Limpia backups antiguos manteniendo solo los más recientes.
        
        Args:
            max_backups: Número máximo de backups a mantener
        """
        try:
            backup_dir = Path.cwd() / "backups"
            
            if not backup_dir.exists():
                return
            
            # Obtener todos los backups ordenados por fecha
            backups = sorted(
                [d for d in backup_dir.iterdir() if d.is_dir()],
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            
            # Eliminar backups antiguos
            for backup in backups[max_backups:]:
                shutil.rmtree(backup)
                logger.info(f"Backup eliminado: {backup}")
                
        except Exception as e:
            logger.error(f"Error limpiando backups: {e}")
