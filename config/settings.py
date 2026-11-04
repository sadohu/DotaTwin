"""
Configuración centralizada de la aplicación DotaTwin.

Este módulo contiene todas las configuraciones y constantes de la aplicación,
siguiendo el principio de separación de responsabilidades.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# ═══════════════════════════════════════════════════════════════════════════
# INFORMACIÓN DE LA APLICACIÓN
# ═══════════════════════════════════════════════════════════════════════════

APP_NAME = "DotaTwin"
APP_VERSION = "3.3.0"
VERSION = APP_VERSION  # Alias para compatibilidad
APP_AUTHOR = "Sadohu"
APP_DESCRIPTION = "Twin your Dota experience - Copy configurations between Steam accounts"

# ═══════════════════════════════════════════════════════════════════════════
# DETECCIÓN DE ENTORNO Y RUTAS DEL SISTEMA
# ═══════════════════════════════════════════════════════════════════════════

def _get_base_path():
    """
    Detecta si estamos en un ejecutable empaquetado o en desarrollo.
    
    Returns:
        Path: Ruta base de la aplicación
    """
    if getattr(sys, 'frozen', False):
        # Estamos en un ejecutable empaquetado con PyInstaller
        return Path(sys.executable).parent
    else:
        # Estamos en desarrollo
        return Path(__file__).parent.parent

def _get_resource_path(relative_path: str) -> Path:
    """
    Obtiene la ruta correcta de un recurso, tanto en desarrollo como empaquetado.
    
    Args:
        relative_path: Ruta relativa al recurso
        
    Returns:
        Path: Ruta absoluta al recurso
    """
    if getattr(sys, 'frozen', False):
        # En ejecutable empaquetado, los recursos están en el directorio temporal
        base_path = Path(sys._MEIPASS)  # Directorio temporal de PyInstaller
        return base_path / relative_path
    else:
        # En desarrollo, usar rutas normales del proyecto
        return PROJECT_ROOT / "config" / "assets" / relative_path

# Rutas base del proyecto
PROJECT_ROOT = _get_base_path()
ASSETS_DIR = PROJECT_ROOT / "config" / "assets"
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"

# Respaldos: siempre junto al exe (o en la raíz del proyecto en desarrollo)
BACKUPS_DIR = PROJECT_ROOT / "backups"
MAX_BACKUPS_PER_ACCOUNT = 5

# Rutas de Steam (Windows)
STEAM_USERDATA_PATH = Path(r"C:\Program Files (x86)\Steam\userdata")
AVATAR_CACHE_PATH = Path(r"C:\Program Files (x86)\Steam\config\avatarcache")

# Archivos de configuración
CACHE_FILE = "ultima_seleccion.json"
ICON_PATH = _get_resource_path("dota2.ico")  # Usar función de detección de rutas
LOG_FILE = "app.log"

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIONES DE LA INTERFAZ
# ═══════════════════════════════════════════════════════════════════════════

# Configuraciones de paginación
DEFAULT_ITEMS_PER_PAGE = 10
ITEMS_PER_PAGE = DEFAULT_ITEMS_PER_PAGE  # Alias para compatibilidad
MIN_ITEMS_PER_PAGE = 5
MAX_ITEMS_PER_PAGE = 50
ITEMS_PER_PAGE_OPTIONS = [10, 15, 20, 25, 30]

# Dimensiones de la ventana
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 800
WINDOW_DEFAULT_WIDTH = 1000
WINDOW_DEFAULT_HEIGHT = 800

# Configuraciones de imagen
AVATAR_SIZE = (32, 32)
DEFAULT_AVATAR_COLOR = (64, 64, 64)

# ═══════════════════════════════════════════════════════════════════════════
# ESTILOS Y COLORES
# ═══════════════════════════════════════════════════════════════════════════

# Los colores de la interfaz (temas oscuro y claro) están en src/utils/theme.py

# Iconos Unicode para la interfaz
ICONS = {
    # Botones principales
    "origen": "📤",
    "destino": "📥",
    "ignorar": "🚫",
    "restaurar": "↩️",
    "copiar": "📋",
    "cancelar": "❌",
    
    # Navegación
    "anterior": "⬅️",
    "siguiente": "➡️",
    
    # Títulos e información
    "cuentas": "🎮",
    "ignoradas": "🔕",
    "pagina": "📄",
    "configuracion": "⚙️",
    "info": "ℹ️",
    "warning": "⚠️",
    "error": "❌",
    "success": "✅"
}

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIONES DE JUEGO
# ═══════════════════════════════════════════════════════════════════════════

# ID de Dota 2 en Steam
DOTA2_APP_ID = "570"

# Patrones de archivos a copiar
CONFIG_PATTERNS = [
    "*.cfg",
    "*.vcfg",  # Valve Configuration Files (configuraciones principales de Dota 2)
    "*.vdf",
    "*.dat",
    "*.txt"
]

# Carpetas a excluir durante la copia
EXCLUDE_FOLDERS = [
    "temp",
    "cache",
    "logs"
]

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIONES DE LOGGING
# ═══════════════════════════════════════════════════════════════════════════

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "standard"
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOG_FILE,
            "formatter": "detailed"
        }
    },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURACIONES POR DEFECTO
# ═══════════════════════════════════════════════════════════════════════════

DEFAULT_CONFIG = {
    "origen": "",
    "destino": "",
    "cuentas_ignoradas": [],
    "items_por_pagina": DEFAULT_ITEMS_PER_PAGE,
    "window_geometry": f"{WINDOW_DEFAULT_WIDTH}x{WINDOW_DEFAULT_HEIGHT}",
    "auto_backup": True,
    "show_confirmations": True
}

# ═══════════════════════════════════════════════════════════════════════════
# MENSAJES DE LA APLICACIÓN
# ═══════════════════════════════════════════════════════════════════════════

MESSAGES = {
    "confirm_ignore": "Dejará de aparecer en la lista. Podrás recuperarla cuando quieras desde la pestaña Cuentas Ignoradas.",
    "confirm_copy": "La configuración actual de {destino} se reemplazará por la de {origen}.\n\nAntes de copiar se guarda un respaldo de {destino}.",
    "success_copy": "Entra a Steam con {destino} y abre Dota 2: tendrás las mismas teclas, héroes y ajustes que {origen}.",
    "error_same_account": "Origen y destino no pueden ser iguales.",
    "select_accounts": "Selecciona origen y destino",
    "ready_to_copy": "Listo para copiar de '{}' a '{}'",
    "no_accounts": "No se encontraron cuentas de Steam con Dota 2",
    "no_ignored_accounts": "No hay cuentas ignoradas",
    "error_steam_path": "No se encontró la instalación de Steam en la ruta estándar",
    "error_permissions": "Error de permisos. Ejecuta como administrador.",
    "error_dota_running": "Si Dota 2 sigue abierto, al cerrarse puede reemplazar la configuración copiada. Steam sí puede quedarse abierto.",
    "error_copy_failed": "Error copiando archivos: {}"
}

def get_config_value(key: str, default: Any = None) -> Any:
    """
    Obtiene un valor de configuración.
    
    Args:
        key: Clave de configuración
        default: Valor por defecto si no existe la clave
        
    Returns:
        Valor de configuración
    """
    return DEFAULT_CONFIG.get(key, default)

def validate_steam_paths() -> bool:
    """
    Valida que las rutas de Steam existan.
    
    Returns:
        True si las rutas son válidas
    """
    return STEAM_USERDATA_PATH.exists() and AVATAR_CACHE_PATH.exists()
