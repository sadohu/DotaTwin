"""
Componentes de interfaz de usuario para la pestaña de cuentas ignoradas.

Este módulo contiene los componentes específicos de la pestaña
de gestión de cuentas ignoradas.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional
from ..models.domain_models import SteamAccount, PaginationInfo
from ..utils.ui_utils import AvatarManager, IconHelper, PaginationWidget, StyleManager
from ..utils.logging_utils import LoggingMixin
from ..utils.theme import palette


class IgnoredAccountRowWidget(LoggingMixin):
    """
    Widget para mostrar una fila de cuenta ignorada.
    
    Similar a AccountRowWidget pero específico para cuentas ignoradas.
    """
    
    def __init__(self, parent: tk.Widget, account: SteamAccount,
                 avatar_manager: AvatarManager):
        """
        Inicializa el widget de fila de cuenta ignorada.
        
        Args:
            parent: Widget padre
            account: Cuenta ignorada a mostrar
            avatar_manager: Gestor de avatares
        """
        self.account = account
        self.avatar_manager = avatar_manager
        
        # Callback para restaurar cuenta
        self.on_restore_account: Optional[Callable[[SteamAccount], None]] = None
        
        # Crear frame principal
        self.frame = ttk.Frame(parent, padding=5)
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Crea todos los widgets de la fila."""
        # Avatar
        avatar = self.avatar_manager.get_avatar(self.account)
        self.avatar_label = tk.Label(self.frame, image=avatar)
        self.avatar_label.grid(row=0, column=0, padx=5)
        
        # Información de la cuenta
        info_text = self.account.display_name
        self.info_label = tk.Label(self.frame, text=info_text, anchor='w')
        self.info_label.grid(row=0, column=1, sticky='w', padx=10)
        
        # Botón restaurar
        self.btn_restaurar = IconHelper.create_icon_button(
            self.frame, "restaurar", "Restaurar",
            self._on_restaurar_clicked
        )
        self.btn_restaurar.grid(row=0, column=2, padx=5)
        
        # Configurar expansión de columnas
        self.frame.columnconfigure(1, weight=1)
    
    def _on_restaurar_clicked(self) -> None:
        """Maneja el clic en el botón restaurar."""
        if self.on_restore_account:
            self.on_restore_account(self.account)
            self.log_method_call("restore_account", account=self.account.steamid)
    
    def pack(self, **kwargs) -> None:
        """Empaqueta el frame principal."""
        self.frame.pack(fill='x', padx=5, pady=3, **kwargs)
    
    def destroy(self) -> None:
        """Destruye el widget."""
        self.frame.destroy()


class IgnoredAccountsListWidget(LoggingMixin):
    """
    Widget principal para mostrar la lista de cuentas ignoradas.
    
    Maneja la visualización de cuentas ignoradas con paginación.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Inicializa el widget de lista de cuentas ignoradas.
        
        Args:
            parent: Widget padre
        """
        self.parent = parent
        
        # Datos
        self.accounts: List[SteamAccount] = []
        self.current_accounts: List[SteamAccount] = []
        self.pagination = PaginationInfo()
        
        # Manager de avatares
        self.avatar_manager = AvatarManager()
        
        # Widgets de cuenta actuales
        self.account_widgets: List[IgnoredAccountRowWidget] = []
        
        # Callbacks
        self.on_account_restored: Optional[Callable[[SteamAccount], None]] = None
        
        # Crear interfaz
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Crea todos los widgets del componente."""
        # Título
        title_text = IconHelper.text_with_icon("ignoradas", "Cuentas ignoradas")
        self.title_label = tk.Label(
            self.parent,
            text=title_text,
            font=("Arial", 12, "bold")
        )
        self.title_label.pack(pady=10)
        
        # Frame scrollable para cuentas
        self.accounts_frame = ttk.Frame(self.parent)
        self.accounts_frame.pack(fill='both', expand=True, padx=5)
        
        # Frame para navegación de páginas
        self.navigation_frame = ttk.Frame(self.parent)
        self.navigation_frame.pack(fill='x', padx=5, pady=5)
        
        # Widget de paginación
        self.pagination_widget = PaginationWidget(
            self.navigation_frame,
            self.pagination,
            self._on_page_changed
        )
    
    def set_accounts(self, accounts: List[SteamAccount]) -> None:
        """
        Establece la lista de cuentas ignoradas a mostrar.
        
        Args:
            accounts: Lista de cuentas ignoradas
        """
        self.accounts = accounts.copy()
        self.pagination.total_items = len(accounts)
        
        # Precargar avatares
        self.avatar_manager.preload_avatars(accounts)
        
        self._update_display()
        self.log_method_call("set_accounts", count=len(accounts))
    
    def set_items_per_page(self, items_per_page: int) -> None:
        """
        Establece el número de elementos por página.
        
        Args:
            items_per_page: Número de elementos por página
        """
        self.pagination.items_per_page = items_per_page
        self.pagination.set_page(1)  # Volver a primera página
        self._update_display()
    
    def _update_display(self) -> None:
        """Actualiza la visualización de cuentas."""
        # Limpiar widgets existentes
        self._clear_account_widgets()
        
        if not self.accounts:
            self._show_empty_message()
            self._hide_navigation()
            return
        
        # Obtener cuentas de la página actual
        self.current_accounts = self.pagination.get_page_items(self.accounts)
        
        # Crear widgets para cuentas actuales
        for account in self.current_accounts:
            widget = self._create_account_widget(account)
            self.account_widgets.append(widget)
        
        # Actualizar navegación
        self._update_navigation()
    
    def _create_account_widget(self, account: SteamAccount) -> IgnoredAccountRowWidget:
        """Crea un widget para una cuenta ignorada específica."""
        widget = IgnoredAccountRowWidget(
            self.accounts_frame,
            account,
            self.avatar_manager
        )
        
        # Configurar callback
        widget.on_restore_account = self._on_restore_account
        
        # Mostrar widget
        widget.pack()
        
        return widget
    
    def _clear_account_widgets(self) -> None:
        """Limpia todos los widgets de cuenta."""
        for widget in self.account_widgets:
            widget.destroy()
        self.account_widgets.clear()
    
    def _show_empty_message(self) -> None:
        """Muestra mensaje cuando no hay cuentas ignoradas."""
        empty_label = tk.Label(
            self.accounts_frame,
            text="No hay cuentas ignoradas",
            font=("Arial", 10),
            fg=palette()["muted"]
        )
        empty_label.pack(pady=20)
        self.account_widgets.append(empty_label)  # Para poder limpiarlo después
    
    def _hide_navigation(self) -> None:
        """Oculta los controles de navegación."""
        self.navigation_frame.pack_forget()
    
    def _update_navigation(self) -> None:
        """Actualiza los controles de navegación."""
        if self.pagination.total_pages > 1:
            self.navigation_frame.pack(fill='x', padx=5, pady=5)
            self.pagination_widget.render()
        else:
            self._hide_navigation()
    
    def _on_restore_account(self, account: SteamAccount) -> None:
        """Maneja la solicitud de restaurar cuenta."""
        if self.on_account_restored:
            self.on_account_restored(account)
    
    def _on_page_changed(self, new_page: int) -> None:
        """Maneja el cambio de página."""
        self.pagination.set_page(new_page)
        self._update_display()


class IgnoredTabController(LoggingMixin):
    """
    Controlador para la pestaña de cuentas ignoradas.
    
    Coordina la interacción entre los widgets y la lógica de negocio.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Inicializa el controlador de la pestaña ignoradas.
        
        Args:
            parent: Widget padre (frame de la pestaña)
        """
        self.parent = parent
        
        # Crear widget principal
        self.accounts_list = IgnoredAccountsListWidget(parent)
        self.accounts_list.on_account_restored = self._on_account_restored
        
        # Callbacks externos
        self.on_account_restored: Optional[Callable[[SteamAccount], None]] = None
    
    def set_ignored_accounts(self, accounts: List[SteamAccount]) -> None:
        """
        Establece las cuentas ignoradas a mostrar.
        
        Args:
            accounts: Lista de cuentas ignoradas
        """
        self.accounts_list.set_accounts(accounts)
        self.log_method_call("set_ignored_accounts", count=len(accounts))
    
    def set_items_per_page(self, items_per_page: int) -> None:
        """
        Actualiza el número de elementos por página.
        
        Args:
            items_per_page: Número de elementos por página
        """
        self.accounts_list.set_items_per_page(items_per_page)
    
    def _on_account_restored(self, account: SteamAccount) -> None:
        """
        Maneja la restauración de una cuenta.
        
        Args:
            account: Cuenta a restaurar
        """
        from ..utils.ui_utils import MessageHelper
        
        # Confirmar restauración
        confirm = MessageHelper.ask_confirmation(
            "Confirmar restauración",
            f"¿Deseas restaurar la cuenta '{account.nombre}'?\n\n"
            f"Volverá a aparecer en la lista principal."
        )
        
        if confirm and self.on_account_restored:
            self.on_account_restored(account)
            self.log_method_call("account_restored", account=account.steamid)


class SimpleIgnoredTabWidget(LoggingMixin):
    """
    Widget simplificado para la pestaña de cuentas ignoradas.
    
    Versión más simple sin paginación para casos de uso básicos.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Inicializa el widget simple de cuentas ignoradas.
        
        Args:
            parent: Widget padre
        """
        self.parent = parent
        self.accounts: List[SteamAccount] = []
        self.avatar_manager = AvatarManager()
        self.account_widgets: List[IgnoredAccountRowWidget] = []
        
        # Callbacks
        self.on_account_restored: Optional[Callable[[SteamAccount], None]] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Crea la interfaz básica."""
        # Título
        title_text = IconHelper.text_with_icon("ignoradas", "Cuentas ignoradas")
        title_label = tk.Label(
            self.parent,
            text=title_text,
            font=("Arial", 12, "bold")
        )
        title_label.pack(pady=10)
        
        # Frame para las cuentas
        self.accounts_frame = ttk.Frame(self.parent)
        self.accounts_frame.pack(fill='both', expand=True, padx=5)
    
    def set_accounts(self, accounts: List[SteamAccount]) -> None:
        """
        Establece las cuentas ignoradas a mostrar.
        
        Args:
            accounts: Lista de cuentas ignoradas
        """
        self.accounts = accounts.copy()
        self._update_display()
        self.log_method_call("set_accounts", count=len(accounts))
    
    def _update_display(self) -> None:
        """Actualiza la visualización de cuentas."""
        # Limpiar widgets existentes
        self._clear_widgets()
        
        if not self.accounts:
            self._show_empty_message()
            return
        
        # Precargar avatares
        self.avatar_manager.preload_avatars(self.accounts)
        
        # Crear widget para cada cuenta
        for account in self.accounts:
            widget = IgnoredAccountRowWidget(
                self.accounts_frame,
                account,
                self.avatar_manager
            )
            widget.on_restore_account = self._on_restore_account
            widget.pack()
            self.account_widgets.append(widget)
    
    def _clear_widgets(self) -> None:
        """Limpia todos los widgets."""
        for widget in self.account_widgets:
            widget.destroy()
        self.account_widgets.clear()
    
    def _show_empty_message(self) -> None:
        """Muestra mensaje cuando no hay cuentas."""
        empty_label = tk.Label(
            self.accounts_frame,
            text="No hay cuentas ignoradas",
            font=("Arial", 10),
            fg=palette()["muted"]
        )
        empty_label.pack(pady=20)
        self.account_widgets.append(empty_label)
    
    def _on_restore_account(self, account: SteamAccount) -> None:
        """Maneja la restauración de cuenta."""
        from ..utils.ui_utils import MessageHelper
        
        confirm = MessageHelper.ask_confirmation(
            "Confirmar restauración",
            f"¿Deseas restaurar la cuenta '{account.nombre}'?"
        )
        
        if confirm and self.on_account_restored:
            self.on_account_restored(account)
