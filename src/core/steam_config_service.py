"""
Servicio para la configuración y detección de Steam.

Este módulo maneja la configuración de rutas personalizadas de Steam
y la detección automática cuando no se encuentra en rutas predeterminadas.
"""

import os
import tkinter as tk
from tkinter import filedialog, ttk
from typing import Optional, List
from pathlib import Path
from ..models.domain_models import AppConfig
from .steam_service import SteamAccountService
from ..utils.logging_utils import LoggingMixin
from ..utils.theme import palette, apply_title_bar, FONTS


def _messages():
    """Diálogos de la interfaz; se importan al usarse para que el núcleo no cargue la GUI."""
    from ..utils.ui_utils import MessageHelper
    return MessageHelper


class SteamConfigurationService(LoggingMixin):
    """
    Servicio para configurar y detectar la instalación de Steam.
    
    Maneja la configuración de rutas personalizadas y la detección
    automática cuando Steam no se encuentra en ubicaciones estándar.
    """
    
    def __init__(self, config: AppConfig):
        super().__init__()
        self.config = config
        self.steam_service = None
        self._initialize_steam_service()
    
    def _initialize_steam_service(self):
        """Inicializa el servicio de Steam con la configuración actual."""
        self.steam_service = SteamAccountService(self.config.custom_steam_path)
    
    def detect_steam_installation(self) -> bool:
        """
        Detecta automáticamente la instalación de Steam.
        
        Returns:
            True si Steam se detecta correctamente
        """
        # Primero intentar con ruta personalizada si existe
        if self.config.custom_steam_path:
            if self.steam_service._validate_steam_path(self.config.custom_steam_path):
                self.logger.info(f"Steam detectado en ruta personalizada: {self.config.custom_steam_path}")
                return True
            else:
                self.logger.warning(f"Ruta personalizada de Steam no válida: {self.config.custom_steam_path}")
                self.config.custom_steam_path = ""
        
        # Buscar en rutas estándar
        default_paths = self.steam_service.get_default_steam_paths()
        if default_paths:
            steam_path = default_paths[0]
            self.logger.info(f"Steam detectado automáticamente en: {steam_path}")
            return True
        
        self.logger.warning("No se pudo detectar Steam automáticamente")
        return False
    
    def prompt_steam_location(self, parent_window: tk.Tk) -> bool:
        """
        Solicita al usuario que seleccione la ubicación de Steam.
        
        Args:
            parent_window: Ventana padre para el diálogo
            
        Returns:
            True si se seleccionó una ruta válida
        """
        self.logger.info("Solicitando ubicación de Steam al usuario")
        
        # Mostrar mensaje explicativo
        result = _messages().ask_confirmation(
            "Steam no encontrado",
            "Elige la carpeta donde instalaste Steam: es la que contiene steam.exe "
            "y las carpetas userdata y steamapps.",
            heading="No se encontró Steam automáticamente",
            confirm_text="Elegir carpeta", cancel_text="Ahora no"
        )
        
        if not result:
            return False
        
        # Abrir diálogo de selección de carpeta
        steam_path = filedialog.askdirectory(
            parent=parent_window,
            title="Seleccionar carpeta de Steam",
            initialdir="C:\\Program Files (x86)"
        )
        
        if not steam_path:
            return False
        
        # Validar la ruta seleccionada
        if self.steam_service._validate_steam_path(steam_path):
            self.config.custom_steam_path = steam_path
            self._initialize_steam_service()
            
            _messages().show_info("Steam configurado", steam_path, "success",
                                    heading="Steam configurado correctamente")

            self.logger.info(f"Usuario configuró Steam en: {steam_path}")
            return True
        else:
            _messages().show_error(
                "Carpeta no válida",
                "Elige la carpeta principal de Steam, la que contiene steam.exe "
                "y las carpetas userdata y steamapps.",
                heading="Esa carpeta no es la de Steam"
            )
            return False
    
    def show_steam_configuration_dialog(self, parent_window: tk.Tk) -> Optional[str]:
        """
        Muestra un diálogo para configurar la ubicación de Steam.
        
        Args:
            parent_window: Ventana padre
            
        Returns:
            Nueva ruta de Steam si se configuró, None si se canceló
        """
        # Si no hay ruta propia, mostrar la que se detectó automáticamente
        current_path = self.config.custom_steam_path
        userdata = getattr(self.steam_service, "steam_userdata_path", None)
        if not current_path and userdata:
            current_path = str(Path(userdata).parent)
        dialog = SteamConfigDialog(parent_window, current_path)
        result = dialog.show()
        
        if result:
            if self.steam_service._validate_steam_path(result):
                self.config.custom_steam_path = result
                self._initialize_steam_service()
                self.logger.info(f"Steam reconfigurado a: {result}")
                return result
            else:
                _messages().show_error(
                    "Carpeta no válida",
                    "Elige la carpeta principal de Steam, la que contiene steam.exe.",
                    heading="Esa carpeta no es la de Steam"
                )

        return None
    
    def get_steam_accounts(self) -> List:
        """
        Obtiene las cuentas de Steam usando la configuración actual.
        
        Returns:
            Lista de cuentas Steam encontradas
        """
        if not self.steam_service:
            return []
        
        return self.steam_service.find_accounts_with_dota2()


class SteamConfigDialog:
    """
    Diálogo para configurar la ubicación de Steam.
    """
    
    def __init__(self, parent: tk.Tk, current_path: str = ""):
        self.parent = parent
        self.current_path = current_path
        self.result = None
        self.dialog = None
    
    def show(self) -> Optional[str]:
        """
        Muestra el diálogo y retorna la ruta seleccionada.
        
        Returns:
            Ruta seleccionada o None si se canceló
        """
        colors = palette()
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Configurar Steam")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg=colors["bg"])
        self.dialog.transient(self.parent)
        try:
            from config.settings import ICON_PATH
            self.dialog.iconbitmap(str(ICON_PATH))
        except Exception:
            pass
        
        self._create_widgets()
        self.dialog.bind("<Escape>", lambda e: self._cancel())
        self.dialog.protocol("WM_DELETE_WINDOW", self._cancel)
        
        # Centrar sobre la ventana principal
        self.dialog.update_idletasks()
        width, height = self.dialog.winfo_reqwidth(), self.dialog.winfo_reqheight()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - height) // 3
        self.dialog.geometry(f"+{max(x, 0)}+{max(y, 0)}")
        apply_title_bar(self.dialog)
        self.dialog.grab_set()
        
        # Esperar hasta que se cierre el diálogo
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        colors = palette()
        main_frame = tk.Frame(self.dialog, bg=colors["bg"], padx=22, pady=18)
        main_frame.pack(fill="both", expand=True)
        
        tk.Label(main_frame, text="¿Dónde está instalado Steam?", font=FONTS["dialog_title"],
                 bg=colors["bg"], fg=colors["fg"]).pack(anchor="w")
        tk.Label(main_frame, text="DotaTwin lo necesita para encontrar tus cuentas. "
                                  "Normalmente se detecta solo.",
                 font=FONTS["dialog"], bg=colors["bg"], fg=colors["muted"],
                 justify="left", wraplength=440).pack(anchor="w", pady=(4, 14))
        
        # Ruta actual
        tk.Label(main_frame, text="CARPETA DE STEAM", font=FONTS["chip_label"],
                 bg=colors["bg"], fg=colors["muted"]).pack(anchor="w")
        self.path_var = tk.StringVar(value=self.current_path or "Sin configurar")
        tk.Label(main_frame, textvariable=self.path_var, font=FONTS["dialog"],
                 bg=colors["input"], fg=colors["fg"], anchor="w", padx=10, pady=7,
                 highlightthickness=1, highlightbackground=colors["border"],
                 width=52).pack(fill="x", pady=(4, 10))
        
        # Acciones sobre la ruta
        button_frame = tk.Frame(main_frame, bg=colors["bg"])
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Detectar automáticamente", style="Accent.TButton",
                   command=self._auto_detect).pack(side="left")
        ttk.Button(button_frame, text="Elegir carpeta...", style="Dialog.TButton",
                   command=self._manual_select).pack(side="left", padx=8)
        
        # Pie con Cancelar / Guardar
        footer = tk.Frame(self.dialog, bg=colors["surface"], padx=16, pady=12)
        footer.pack(fill="x")
        ttk.Button(footer, text="Guardar", style="Success.TButton",
                   command=self._accept).pack(side="right", padx=(8, 0))
        ttk.Button(footer, text="Cancelar", style="Dialog.TButton",
                   command=self._cancel).pack(side="right")
    
    def _auto_detect(self):
        """Detecta automáticamente Steam."""
        steam_service = SteamAccountService()
        paths = steam_service.get_default_steam_paths()
        
        if paths:
            self.current_path = paths[0]
            # La ruta encontrada aparece en el campo; no hace falta otro aviso
            self.path_var.set(self.current_path)
        else:
            _messages().show_warning(
                "Steam no detectado",
                "Usa Elegir carpeta... para indicarla a mano.",
                heading="No se encontró Steam automáticamente"
            )
    
    def _manual_select(self):
        """Permite seleccionar manualmente la carpeta de Steam."""
        steam_path = filedialog.askdirectory(
            parent=self.dialog,
            title="Seleccionar carpeta de Steam",
            initialdir=self.current_path if self.current_path else "C:\\Program Files (x86)"
        )
        
        if steam_path:
            steam_service = SteamAccountService()
            if steam_service._validate_steam_path(steam_path):
                self.current_path = steam_path
                self.path_var.set(steam_path)
            else:
                _messages().show_error(
                    "Carpeta no válida",
                    "Elige la carpeta principal de Steam, la que contiene steam.exe.",
                    heading="Esa carpeta no es la de Steam"
                )
    
    def _accept(self):
        """Acepta la configuración actual."""
        if self.current_path and self.current_path != "No configurada":
            self.result = self.current_path
        self.dialog.destroy()
    
    def _cancel(self):
        """Cancela el diálogo."""
        self.result = None
        self.dialog.destroy()
