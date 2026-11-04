"""
Servicios de negocio para la detección y gestión de cuentas Steam.

Este módulo implementa la lógica de negocio para detectar cuentas de Steam
con Dota 2 y extraer información relevante.
"""

import os
import re
import logging
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from ..models.domain_models import SteamAccount
from config.settings import STEAM_USERDATA_PATH, AVATAR_CACHE_PATH, DOTA2_APP_ID

logger = logging.getLogger(__name__)


class SteamAccountService:
    """
    Servicio para detectar y gestionar cuentas de Steam.
    
    Implementa la lógica de detección automática de cuentas
    y extracción de información de usuario.
    """
    
    def __init__(self, custom_steam_path: str = ""):
        self.custom_steam_path = custom_steam_path
        self.steam_userdata_path = self._get_steam_userdata_path()
        self.avatar_cache_path = AVATAR_CACHE_PATH
        self.dota2_app_id = DOTA2_APP_ID
    
    def _get_steam_userdata_path(self) -> str:
        """
        Obtiene la ruta de userdata de Steam, usando ruta personalizada si está configurada.
        
        Returns:
            Ruta del directorio userdata de Steam
        """
        if self.custom_steam_path and os.path.exists(self.custom_steam_path):
            return Path(self.custom_steam_path) / "userdata"
        return Path(STEAM_USERDATA_PATH)
    
    def set_custom_steam_path(self, steam_path: str) -> bool:
        """
        Configura una ruta personalizada de Steam.
        
        Args:
            steam_path: Ruta del directorio de Steam
            
        Returns:
            True si la ruta es válida
        """
        if self._validate_steam_path(steam_path):
            self.custom_steam_path = str(Path(steam_path))
            self.steam_userdata_path = Path(steam_path) / "userdata"
            logger.info(f"Ruta de Steam configurada: {steam_path}")
            return True
        return False
    
    def _validate_steam_path(self, steam_path: str) -> bool:
        """
        Valida si una ruta contiene una instalación válida de Steam.
        
        Args:
            steam_path: Ruta a validar
            
        Returns:
            True si es una instalación válida de Steam
        """
        if not steam_path or not os.path.exists(steam_path):
            return False
            
        # Verificar archivos/directorios críticos de Steam
        steam_exe = os.path.join(steam_path, "steam.exe")
        userdata_dir = os.path.join(steam_path, "userdata")
        steamapps_dir = os.path.join(steam_path, "steamapps")
        
        return (os.path.exists(steam_exe) or os.path.exists(userdata_dir)) and \
               os.path.exists(steamapps_dir)
    
    def get_default_steam_paths(self) -> List[str]:
        """
        Obtiene una lista de rutas típicas donde puede estar instalado Steam.
        
        Returns:
            Lista de rutas potenciales de Steam
        """
        potential_paths = [
            r"C:\Program Files (x86)\Steam",
            r"C:\Program Files\Steam",
            r"D:\Steam",
            r"E:\Steam",
            r"F:\Steam",
            # Steam desde Microsoft Store
            os.path.expanduser(r"~\AppData\Local\Packages\ValveCorporation.Steam_*"),
        ]
        
        valid_paths = []
        for path in potential_paths:
            if "*" in path:
                # Manejar wildcards para Steam de Microsoft Store
                import glob
                for expanded_path in glob.glob(path):
                    steam_path = os.path.join(expanded_path, "LocalCache", "Local", "Steam")
                    if self._validate_steam_path(steam_path):
                        valid_paths.append(steam_path)
            elif self._validate_steam_path(path):
                valid_paths.append(path)
        
        return valid_paths
    
    def find_accounts_with_dota2(self) -> List[SteamAccount]:
        """
        Detecta todas las cuentas de Steam que tienen Dota 2 instalado.
        
        Returns:
            Lista de cuentas Steam con Dota 2
        """
        accounts = []
        
        if not self._validate_steam_installation():
            logger.warning("Instalación de Steam no encontrada o inválida")
            return accounts
        
        # No se lee config/loginusers.vdf: los antivirus (ej. Kaspersky) suspenden
        # ejecutables sin firma que lo abren, porque es lo que hacen los robacuentas.
        # Steam crea userdata/<id> al iniciar sesión, así que basta con esa carpeta.
        try:
            for folder in os.listdir(self.steam_userdata_path):
                account = self._process_steam_folder(folder)
                if account:
                    accounts.append(account)
                    logger.debug(f"Cuenta encontrada: {account.display_name}")

        except (OSError, PermissionError) as e:
            logger.error(f"Error accediendo a userdata de Steam: {e}")

        logger.info(f"Se encontraron {len(accounts)} cuentas de Steam")
        return accounts
    
    def _validate_steam_installation(self) -> bool:
        """
        Valida que la instalación de Steam sea accesible.
        
        Returns:
            True si Steam está correctamente instalado
        """
        return (self.steam_userdata_path.exists() and 
                self.avatar_cache_path.exists())
    
    def _process_steam_folder(self, folder_name: str) -> Optional[SteamAccount]:
        """
        Procesa una carpeta de usuario de Steam.

        La carpeta 570 no se crea aquí: se crea al copiar hacia la cuenta.

        Args:
            folder_name: Nombre de la carpeta de usuario

        Returns:
            SteamAccount de la carpeta, None si no es una carpeta de usuario
        """
        try:
            if not folder_name.isdigit():
                return None

            user_path = self.steam_userdata_path / folder_name
            if not user_path.is_dir():
                return None

            dota_path = user_path / self.dota2_app_id

            # Extraer información del usuario
            nombre = self._extract_username(user_path)
            avatar_path = self._find_avatar(folder_name)
            
            return SteamAccount(
                steamid=folder_name,
                nombre=nombre,
                ruta=dota_path,
                avatar=avatar_path
            )
            
        except (ValueError, OSError) as e:
            logger.debug(f"Error procesando carpeta {folder_name}: {e}")
            return None
    
    def _extract_username(self, user_path: Path) -> str:
        """
        Extrae el nombre de usuario desde localconfig.vdf.
        
        Args:
            user_path: Ruta de la carpeta del usuario
            
        Returns:
            Nombre del usuario o "Desconocido"
        """
        config_path = user_path / "config" / "localconfig.vdf"
        
        if not config_path.exists():
            return "Desconocido"
        
        try:
            with open(config_path, encoding='utf-8', errors='ignore') as f:
                contenido = f.read()
                
            # Buscar el nombre de usuario en el archivo VDF
            match = re.search(r'"PersonaName"\s+"([^"]+)"', contenido)
            if match:
                return match.group(1)
                
        except (IOError, UnicodeDecodeError) as e:
            logger.debug(f"Error leyendo localconfig.vdf: {e}")
        
        return "Desconocido"
    
    def _find_avatar(self, steamid: str) -> Optional[Path]:
        """
        Busca el avatar de una cuenta en el caché de Steam.
        
        Args:
            steamid: Steam ID de la cuenta
            
        Returns:
            Ruta del avatar si existe, None en caso contrario
        """
        try:
            # Convertir Steam3 ID a SteamID64
            steam3_id = int(steamid)
            steamid64 = str(steam3_id + 76561197960265728)
            
            avatar_path = self.avatar_cache_path / f"{steamid64}.png"
            
            if avatar_path.exists():
                return avatar_path
                
        except (ValueError, OSError) as e:
            logger.debug(f"Error buscando avatar para {steamid}: {e}")
        
        return None
    
    def refresh_account_info(self, account: SteamAccount) -> SteamAccount:
        """
        Actualiza la información de una cuenta específica.
        
        Args:
            account: Cuenta a actualizar
            
        Returns:
            Cuenta con información actualizada
        """
        updated_account = self._process_steam_folder(account.steamid)
        return updated_account if updated_account else account
    
    def validate_account(self, account: SteamAccount) -> bool:
        """
        Valida que una cuenta tenga configuración válida de Dota 2.
        
        Args:
            account: Cuenta a validar
            
        Returns:
            True si la cuenta es válida
        """
        return (account.config_exists and 
                account.ruta.is_dir() and
                len(list(account.ruta.iterdir())) > 0)


class AccountFilterService:
    """
    Servicio para filtrar y organizar cuentas.
    
    Proporciona métodos para filtrar cuentas según diferentes criterios.
    """
    
    @staticmethod
    def filter_available_accounts(accounts: List[SteamAccount], 
                                ignored_ids: List[str]) -> List[SteamAccount]:
        """
        Filtra cuentas disponibles (no ignoradas).
        
        Args:
            accounts: Lista completa de cuentas
            ignored_ids: IDs de cuentas ignoradas
            
        Returns:
            Lista de cuentas no ignoradas
        """
        return [account for account in accounts 
                if account.steamid not in ignored_ids]
    
    @staticmethod
    def filter_ignored_accounts(accounts: List[SteamAccount], 
                              ignored_ids: List[str]) -> List[SteamAccount]:
        """
        Filtra cuentas ignoradas.
        
        Args:
            accounts: Lista completa de cuentas
            ignored_ids: IDs de cuentas ignoradas
            
        Returns:
            Lista de cuentas ignoradas
        """
        return [account for account in accounts 
                if account.steamid in ignored_ids]
    
    @staticmethod
    def find_account_by_id(accounts: List[SteamAccount], 
                          steamid: str) -> Optional[SteamAccount]:
        """
        Busca una cuenta por su Steam ID.
        
        Args:
            accounts: Lista de cuentas
            steamid: ID a buscar
            
        Returns:
            Cuenta encontrada o None
        """
        for account in accounts:
            if account.steamid == steamid:
                return account
        return None
    
    @staticmethod
    def sort_accounts(accounts: List[SteamAccount], 
                     sort_by: str = "nombre") -> List[SteamAccount]:
        """
        Ordena cuentas según un criterio.
        
        Args:
            accounts: Lista de cuentas
            sort_by: Criterio de ordenamiento ("nombre", "steamid")
            
        Returns:
            Lista ordenada de cuentas
        """
        if sort_by == "nombre":
            return sorted(accounts, key=lambda a: a.nombre.lower())
        elif sort_by == "steamid":
            return sorted(accounts, key=lambda a: a.steamid)
        else:
            return accounts.copy()


class ValidationService:
    """
    Servicio de validación para operaciones de la aplicación.
    
    Centraliza todas las validaciones de negocio.
    """
    
    @staticmethod
    def validate_copy_operation(origen: SteamAccount, 
                              destino: SteamAccount) -> Tuple[bool, str]:
        """
        Valida que una operación de copia sea posible.
        
        Args:
            origen: Cuenta origen
            destino: Cuenta destino
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if origen == destino:
            return False, "Origen y destino no pueden ser iguales"
        
        if not origen.config_exists:
            return False, f"No existe configuración en la cuenta origen: {origen.nombre}"
        
        if not destino.ruta.parent.parent.exists():
            return False, f"No se puede acceder a la cuenta destino: {destino.nombre}"

        return True, ""

    @staticmethod
    def find_running_steam_processes() -> List[str]:
        """
        Busca procesos de Steam o Dota 2 en ejecución.

        Mientras están abiertos pueden sobrescribir la configuración copiada
        al sincronizar con Steam Cloud.

        Returns:
            Lista de procesos en ejecución (ej: ["steam.exe"])
        """
        running = []

        for process_name in ("steam.exe", "dota2.exe"):
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {process_name}", "/FO", "CSV", "/NH"],
                    capture_output=True, text=True, errors="ignore",
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                )
                if f'"{process_name}"' in result.stdout.lower():
                    running.append(process_name)

            except OSError as e:
                logger.warning(f"No se pudo verificar el proceso {process_name}: {e}")

        return running
    
    @staticmethod
    def validate_steam_paths() -> Tuple[bool, str]:
        """
        Valida que las rutas de Steam sean accesibles.
        
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        if not STEAM_USERDATA_PATH.exists():
            return False, "No se encontró la carpeta userdata de Steam"
        
        if not AVATAR_CACHE_PATH.exists():
            return False, "No se encontró el caché de avatares de Steam"
        
        return True, ""
    
    @staticmethod
    def validate_pagination_settings(items_per_page: int) -> Tuple[bool, str]:
        """
        Valida configuraciones de paginación.
        
        Args:
            items_per_page: Número de elementos por página
            
        Returns:
            Tupla (es_valido, mensaje_error)
        """
        from config.settings import MIN_ITEMS_PER_PAGE, MAX_ITEMS_PER_PAGE
        
        if items_per_page < MIN_ITEMS_PER_PAGE:
            return False, f"Mínimo {MIN_ITEMS_PER_PAGE} elementos por página"
        
        if items_per_page > MAX_ITEMS_PER_PAGE:
            return False, f"Máximo {MAX_ITEMS_PER_PAGE} elementos por página"
        
        return True, ""
