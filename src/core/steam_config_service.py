"""
Servicio para la configuración y detección de Steam.

Este módulo maneja la configuración de rutas personalizadas de Steam
y la detección automática cuando no se encuentra en rutas predeterminadas.
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, List
from pathlib import Path
from ..models.domain_models import AppConfig
from .steam_service import SteamAccountService
from ..utils.logging_utils import LoggingMixin
from ..utils.theme import palette, apply_title_bar


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
        result = messagebox.askyesno(
            "Steam no encontrado",
            "No se pudo detectar Steam automáticamente.\\n\\n"
            "¿Desea seleccionar manualmente la carpeta donde está instalado Steam?\\n\\n"
            "Nota: Busque la carpeta que contiene 'steam.exe' y las carpetas 'userdata' y 'steamapps'.",
            icon="question"
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
            
            messagebox.showinfo(
                "Steam configurado",
                f"Steam configurado correctamente en:\\n{steam_path}"
            )
            
            self.logger.info(f"Usuario configuró Steam en: {steam_path}")
            return True
        else:
            messagebox.showerror(
                "Ruta inválida",
                "La carpeta seleccionada no parece contener una instalación válida de Steam.\\n\\n"
                "Asegúrese de seleccionar la carpeta principal de Steam que contiene:\\n"
                "- steam.exe\\n"
                "- carpeta 'userdata'\\n"
                "- carpeta 'steamapps'"
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
        dialog = SteamConfigDialog(parent_window, self.config.custom_steam_path)
        result = dialog.show()
        
        if result:
            if self.steam_service._validate_steam_path(result):
                self.config.custom_steam_path = result
                self._initialize_steam_service()
                self.logger.info(f"Steam reconfigurado a: {result}")
                return result
            else:
                messagebox.showerror(
                    "Ruta inválida",
                    "La ruta seleccionada no contiene una instalación válida de Steam."
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
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Configuración de Steam")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Centrar el diálogo
        self.dialog.geometry("+%d+%d" % (
            self.parent.winfo_rootx() + 50,
            self.parent.winfo_rooty() + 50
        ))
        
        self._create_widgets()
        apply_title_bar(self.dialog)
        
        # Esperar hasta que se cierre el diálogo
        self.dialog.wait_window()
        return self.result
    
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        main_frame = tk.Frame(self.dialog, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Título
        title_label = tk.Label(
            main_frame,
            text="Configuración de Steam",
            font=("Arial", 14, "bold")
        )
        title_label.pack(pady=(0, 15))
        
        # Descripción
        desc_label = tk.Label(
            main_frame,
            text="Configure la ubicación de su instalación de Steam.\\n"
                 "Esto es necesario para detectar las cuentas y configuraciones de Dota 2.",
            justify="left",
            wraplength=450
        )
        desc_label.pack(pady=(0, 15))
        
        # Ruta actual
        current_frame = tk.Frame(main_frame)
        current_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(current_frame, text="Ruta actual:", font=("Arial", 10, "bold")).pack(anchor="w")
        
        self.path_var = tk.StringVar(value=self.current_path or "No configurada")
        path_label = tk.Label(
            current_frame,
            textvariable=self.path_var,
            relief="sunken",
            bg=palette()["input"],
            fg=palette()["fg"],
            anchor="w",
            padx=5,
            pady=5
        )
        path_label.pack(fill="x", pady=(5, 0))
        
        # Botones de acción
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))
        
        # Detectar automáticamente
        auto_btn = tk.Button(
            button_frame,
            text="Detectar automáticamente",
            command=self._auto_detect,
            bg="#4CAF50",
            fg="white",
            padx=20
        )
        auto_btn.pack(side="left", padx=(0, 5))
        
        # Seleccionar manualmente
        manual_btn = tk.Button(
            button_frame,
            text="Seleccionar carpeta...",
            command=self._manual_select,
            bg="#2196F3",
            fg="white",
            padx=20
        )
        manual_btn.pack(side="left", padx=5)
        
        # Botones de diálogo
        dialog_button_frame = tk.Frame(main_frame)
        dialog_button_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = tk.Button(
            dialog_button_frame,
            text="Cancelar",
            command=self._cancel,
            padx=20
        )
        cancel_btn.pack(side="right", padx=(5, 0))
        
        ok_btn = tk.Button(
            dialog_button_frame,
            text="Aceptar",
            command=self._accept,
            bg="#4CAF50",
            fg="white",
            padx=20
        )
        ok_btn.pack(side="right")
    
    def _auto_detect(self):
        """Detecta automáticamente Steam."""
        steam_service = SteamAccountService()
        paths = steam_service.get_default_steam_paths()
        
        if paths:
            self.current_path = paths[0]
            self.path_var.set(self.current_path)
            messagebox.showinfo("Steam detectado", f"Steam encontrado en:\\n{self.current_path}")
        else:
            messagebox.showwarning(
                "Steam no detectado",
                "No se pudo detectar Steam automáticamente.\\n"
                "Use 'Seleccionar carpeta...' para configurarlo manualmente."
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
                messagebox.showerror(
                    "Ruta inválida",
                    "La carpeta seleccionada no contiene una instalación válida de Steam."
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
