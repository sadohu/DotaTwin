"""
Servicio de gestión de configuraciones para Dota 2 Config Copier.

Este módulo maneja la persistencia de configuraciones y operaciones
de copia de archivos siguiendo principios de responsabilidad única.
"""

import os
import re
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from ..models.domain_models import AppConfig, BackupInfo, CopyOperation, SteamAccount
from config.settings import (CACHE_FILE, CONFIG_PATTERNS, EXCLUDE_FOLDERS,
                             BACKUPS_DIR, MAX_BACKUPS_PER_ACCOUNT)

logger = logging.getLogger(__name__)

REMOTECACHE_FILE = "remotecache.vdf"

# Respaldos: backups/backup_<steamid>_<AAAAMMDD>_<HHMMSS>[_n]
BACKUP_TIME_FORMAT = "%Y%m%d_%H%M%S"
BACKUP_NAME_PATTERN = re.compile(r"^backup_(?P<steamid>\d+)_(?P<stamp>\d{8}_\d{6})(?:_\d+)?$")


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
    
    def __init__(self, enable_backup: bool = True, backup_dir: Optional[Path] = None):
        """
        Inicializa el servicio de copia.

        Args:
            enable_backup: Habilita backups automáticos
            backup_dir: Carpeta de respaldos (por defecto, "backups" junto al exe)
        """
        self.enable_backup = enable_backup
        self.backup_dir = Path(backup_dir) if backup_dir else BACKUPS_DIR
    
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
        return self.create_backup(operation.destino.steamid, operation.destino.ruta) is not False

    def create_backup(self, steamid: str, config_path: Path):
        """
        Guarda una copia de la carpeta 570 de una cuenta.

        Args:
            steamid: SteamID de la cuenta
            config_path: Carpeta 570 de la cuenta

        Returns:
            Ruta del respaldo, None si no había nada que respaldar o False si falló
        """
        try:
            if not config_path.is_dir() or not any(config_path.iterdir()):
                return None  # No hay nada que respaldar

            backup_path = self._new_backup_path(steamid)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(config_path, backup_path)
            logger.info(f"Backup creado en: {backup_path}")
            return backup_path

        except (OSError, shutil.Error) as e:
            logger.error(f"Error creando backup: {e}")
            return False

    def _new_backup_path(self, steamid: str) -> Path:
        """Ruta libre backups/backup_<steamid>_<fecha>_<hora> (con sufijo si ya existe)."""
        stamp = datetime.now().strftime(BACKUP_TIME_FORMAT)
        path = self.backup_dir / f"backup_{steamid}_{stamp}"
        counter = 2
        while path.exists():
            path = self.backup_dir / f"backup_{steamid}_{stamp}_{counter}"
            counter += 1
        return path

    def list_backups(self, steamid: Optional[str] = None) -> List[BackupInfo]:
        """
        Lista los respaldos guardados, del más reciente al más antiguo.

        Args:
            steamid: Si se indica, solo los de esa cuenta
        """
        backups = []
        if not self.backup_dir.is_dir():
            return backups

        for folder in self.backup_dir.iterdir():
            match = BACKUP_NAME_PATTERN.match(folder.name)
            if not folder.is_dir() or not match:
                continue
            if steamid and match.group("steamid") != steamid:
                continue
            try:
                created = datetime.strptime(match.group("stamp"), BACKUP_TIME_FORMAT)
            except ValueError:
                continue
            backups.append(BackupInfo(match.group("steamid"), created, folder))

        return sorted(backups, key=lambda b: (b.created, b.path.name), reverse=True)

    def restore_backup(self, backup: BackupInfo, config_path: Path) -> Tuple[bool, str]:
        """
        Restaura un respaldo en la carpeta 570 de su cuenta.

        Antes guarda un respaldo de la configuración actual, para poder deshacerlo.
        Se conserva el remotecache.vdf actual de la cuenta, igual que al copiar.

        Args:
            backup: Respaldo a restaurar
            config_path: Carpeta 570 de la cuenta

        Returns:
            Tupla (éxito, mensaje)
        """
        if not backup.path.is_dir():
            return False, "El respaldo ya no existe."

        if self.create_backup(backup.steamid, config_path) is False:
            return False, "No se pudo guardar la configuración actual antes de restaurar."

        if not self._copy_folder_recursive(backup.path, config_path):
            return False, "No se pudieron copiar los archivos del respaldo."

        logger.info(f"Respaldo restaurado: {backup.path} -> {config_path}")
        return True, "Respaldo restaurado"
    
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
    
    def cleanup_old_backups(self, max_per_account: int = MAX_BACKUPS_PER_ACCOUNT) -> None:
        """
        Borra los respaldos antiguos dejando los más recientes de cada cuenta.

        Args:
            max_per_account: Respaldos que se conservan por cuenta
        """
        try:
            kept: Dict[str, int] = {}
            for backup in self.list_backups():  # del más reciente al más antiguo
                kept[backup.steamid] = kept.get(backup.steamid, 0) + 1
                if kept[backup.steamid] > max_per_account:
                    shutil.rmtree(backup.path)
                    logger.info(f"Backup eliminado: {backup.path}")

        except Exception as e:
            logger.error(f"Error limpiando backups: {e}")
