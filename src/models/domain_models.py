"""
Modelos de datos para la aplicación Dota 2 Config Copier.

Este módulo define las estructuras de datos y entidades del dominio,
siguiendo el patrón Domain-Driven Design (DDD).
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from pathlib import Path
import json


@dataclass
class SteamAccount:
    """
    Representa una cuenta de Steam con Dota 2.
    
    Esta clase encapsula toda la información relevante de una cuenta
    y proporciona métodos para trabajar con ella.
    """
    steamid: str
    nombre: str
    ruta: Path
    avatar: Optional[Path] = None
    
    @property
    def steamid64(self) -> str:
        """Convierte Steam3 ID a SteamID64."""
        try:
            steam3_id = int(self.steamid)
            return str(steam3_id + 76561197960265728)
        except ValueError:
            return self.steamid
    
    @property
    def display_name(self) -> str:
        """Nombre para mostrar en la interfaz."""
        nombre = f"{self.nombre} (SteamID: {self.steamid})"
        return nombre if self.config_exists else f"{nombre} - sin carpeta 570"
    
    @property
    def has_avatar(self) -> bool:
        """Indica si la cuenta tiene un avatar válido."""
        return self.avatar is not None and self.avatar.exists()
    
    @property
    def config_exists(self) -> bool:
        """Indica si existe la carpeta de configuración de Dota 2 y tiene contenido."""
        try:
            return self.ruta.is_dir() and any(self.ruta.iterdir())
        except OSError:
            return False
    
    def __eq__(self, other) -> bool:
        """Compara cuentas por SteamID."""
        if not isinstance(other, SteamAccount):
            return False
        return self.steamid == other.steamid
    
    def __hash__(self) -> int:
        """Hash basado en SteamID para uso en sets y dicts."""
        return hash(self.steamid)
    
    def __str__(self) -> str:
        """Representación string de la cuenta."""
        return self.display_name


@dataclass
class PaginationInfo:
    """
    Información de paginación para la interfaz.
    
    Encapsula la lógica de paginación y cálculos relacionados.
    """
    current_page: int = 1
    items_per_page: int = 10
    total_items: int = 0
    
    @property
    def total_pages(self) -> int:
        """Calcula el número total de páginas."""
        if self.total_items == 0:
            return 1
        return max(1, (self.total_items + self.items_per_page - 1) // self.items_per_page)
    
    @property
    def start_index(self) -> int:
        """Índice de inicio para la página actual."""
        return (self.current_page - 1) * self.items_per_page
    
    @property
    def end_index(self) -> int:
        """Índice de fin para la página actual."""
        return min(self.start_index + self.items_per_page, self.total_items)
    
    @property
    def has_previous(self) -> bool:
        """Indica si existe página anterior."""
        return self.current_page > 1
    
    @property
    def has_next(self) -> bool:
        """Indica si existe página siguiente."""
        return self.current_page < self.total_pages
    
    @property
    def page_info_text(self) -> str:
        """Texto informativo de la página actual."""
        return f"Página {self.current_page} de {self.total_pages} ({self.total_items} elementos)"
    
    def get_page_range(self, window_size: int = 5) -> range:
        """
        Obtiene el rango de páginas a mostrar en la navegación.
        
        Args:
            window_size: Número máximo de páginas a mostrar
            
        Returns:
            Rango de páginas
        """
        start = max(1, self.current_page - window_size // 2)
        end = min(self.total_pages + 1, start + window_size)
        start = max(1, end - window_size)
        return range(start, end)
    
    def set_page(self, page: int) -> None:
        """
        Establece la página actual validando los límites.
        
        Args:
            page: Número de página
        """
        self.current_page = max(1, min(page, self.total_pages))
    
    def next_page(self) -> bool:
        """
        Avanza a la siguiente página.
        
        Returns:
            True si se pudo avanzar
        """
        if self.has_next:
            self.current_page += 1
            return True
        return False
    
    def previous_page(self) -> bool:
        """
        Retrocede a la página anterior.
        
        Returns:
            True si se pudo retroceder
        """
        if self.has_previous:
            self.current_page -= 1
            return True
        return False
    
    def get_page_items(self, items: List[Any]) -> List[Any]:
        """
        Obtiene los elementos de la página actual.
        
        Args:
            items: Lista completa de elementos
            
        Returns:
            Elementos de la página actual
        """
        return items[self.start_index:self.end_index]
    
    def find_item_page(self, items: List[Any], target_item: Any) -> int:
        """
        Encuentra en qué página está un elemento específico.
        
        Args:
            items: Lista de elementos
            target_item: Elemento a buscar
            
        Returns:
            Número de página donde está el elemento
        """
        try:
            index = items.index(target_item)
            return (index // self.items_per_page) + 1
        except ValueError:
            return 1


@dataclass
class AppSelection:
    """
    Representa la selección actual de origen y destino.
    
    Encapsula la lógica de selección y validación.
    """
    origen: Optional[SteamAccount] = None
    destino: Optional[SteamAccount] = None
    
    @property
    def is_valid(self) -> bool:
        """Indica si la selección es válida para copiar."""
        return (self.origen is not None and 
                self.destino is not None and 
                self.origen != self.destino)
    
    @property
    def is_complete(self) -> bool:
        """Indica si se han seleccionado origen y destino."""
        return self.origen is not None and self.destino is not None
    
    @property
    def copy_description(self) -> str:
        """Descripción de la copia a realizar."""
        if not self.is_complete:
            return "Selecciona origen y destino"
        
        if not self.is_valid:
            return "Origen y destino no pueden ser iguales"
        
        return f"Listo para copiar de '{self.origen.nombre}' a '{self.destino.nombre}'"
    
    def clear(self) -> None:
        """Limpia la selección actual."""
        self.origen = None
        self.destino = None
    
    def set_origen(self, account: SteamAccount) -> None:
        """Establece la cuenta origen."""
        self.origen = account
    
    def set_destino(self, account: SteamAccount) -> None:
        """Establece la cuenta destino."""
        self.destino = account
    
    def has_account(self, account: SteamAccount) -> bool:
        """Verifica si una cuenta está en la selección actual."""
        return account == self.origen or account == self.destino


@dataclass
class AppConfig:
    """
    Configuración persistente de la aplicación.
    
    Maneja la carga, guardado y migración de configuraciones.
    """
    origen: str = ""
    destino: str = ""
    cuentas_ignoradas: List[str] = field(default_factory=list)
    items_por_pagina: int = 10
    window_geometry: str = "1000x700"
    auto_backup: bool = True
    show_confirmations: bool = True
    custom_steam_path: str = ""  # Ruta personalizada de Steam
    
    @classmethod
    def load_from_file(cls, file_path: Path) -> 'AppConfig':
        """
        Carga la configuración desde un archivo JSON.
        
        Args:
            file_path: Ruta del archivo de configuración
            
        Returns:
            Instancia de configuración
        """
        if not file_path.exists():
            return cls()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Migración automática de configuraciones antiguas
            migrated_data = cls._migrate_config(data)
            
            return cls(**{k: v for k, v in migrated_data.items() 
                         if k in cls.__dataclass_fields__})
            
        except (json.JSONDecodeError, TypeError, KeyError):
            # Si hay error, crear configuración nueva
            return cls()
    
    def save_to_file(self, file_path: Path) -> bool:
        """
        Guarda la configuración a un archivo JSON.
        
        Args:
            file_path: Ruta del archivo de configuración
            
        Returns:
            True si se guardó correctamente
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            
            return True
            
        except (IOError, OSError):
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario."""
        return {
            "origen": self.origen,
            "destino": self.destino,
            "cuentas_ignoradas": self.cuentas_ignoradas.copy(),
            "items_por_pagina": self.items_por_pagina,
            "window_geometry": self.window_geometry,
            "auto_backup": self.auto_backup,
            "show_confirmations": self.show_confirmations
        }
    
    @staticmethod
    def _migrate_config(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migra configuraciones de versiones anteriores.
        
        Args:
            data: Datos de configuración cargados
            
        Returns:
            Datos migrados
        """
        # Asegurar campos obligatorios
        if "cuentas_ignoradas" not in data:
            data["cuentas_ignoradas"] = []
        
        if "items_por_pagina" not in data:
            data["items_por_pagina"] = 10
        
        if "window_geometry" not in data:
            data["window_geometry"] = "1000x700"
        
        if "auto_backup" not in data:
            data["auto_backup"] = True
        
        if "show_confirmations" not in data:
            data["show_confirmations"] = True
        
        return data
    
    def add_ignored_account(self, steamid: str) -> None:
        """Agrega una cuenta a la lista de ignoradas."""
        if steamid not in self.cuentas_ignoradas:
            self.cuentas_ignoradas.append(steamid)
    
    def remove_ignored_account(self, steamid: str) -> None:
        """Remueve una cuenta de la lista de ignoradas."""
        if steamid in self.cuentas_ignoradas:
            self.cuentas_ignoradas.remove(steamid)
    
    def is_ignored(self, steamid: str) -> bool:
        """Verifica si una cuenta está ignorada."""
        return steamid in self.cuentas_ignoradas
    
    def update_selection(self, origen: str, destino: str) -> None:
        """Actualiza la selección de origen y destino."""
        self.origen = origen
        self.destino = destino


@dataclass
class CopyOperation:
    """
    Representa una operación de copia de configuración.
    
    Encapsula la información necesaria para realizar y validar una copia.
    """
    origen: SteamAccount
    destino: SteamAccount
    backup_enabled: bool = True
    
    @property
    def is_valid(self) -> bool:
        """Valida que la operación de copia sea posible."""
        return (self.origen.config_exists and 
                self.destino.ruta.parent.parent.exists() and
                self.origen != self.destino)
    
    @property
    def description(self) -> str:
        """Descripción de la operación."""
        return f"Copiar configuración: {self.origen.nombre} → {self.destino.nombre}"
    
    def get_backup_path(self) -> Path:
        """Obtiene la ruta de backup para esta operación."""
        timestamp = Path.cwd() / "backups" / f"backup_{self.destino.steamid}_{self.timestamp}"
        return timestamp
    
    @property
    def timestamp(self) -> str:
        """Timestamp para identificar la operación."""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
