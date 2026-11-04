"""
Componentes de interfaz de usuario para la pestaña principal.

Este módulo contiene los componentes específicos de la pestaña
de cuentas disponibles, siguiendo principios de composición.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional
from ..models.domain_models import SteamAccount, PaginationInfo, AppSelection
from ..utils.ui_utils import (
    AvatarManager, IconHelper, PaginationWidget, 
    MessageHelper, WidgetFactory, StyleManager
)
from ..utils.logging_utils import LoggingMixin
from ..utils.theme import palette
from config.settings import ITEMS_PER_PAGE_OPTIONS


class AccountRowWidget(LoggingMixin):
    """
    Widget para mostrar una fila de cuenta individual.
    
    Encapsula la presentación y comportamiento de una cuenta en la lista.
    """
    
    def __init__(self, parent: tk.Widget, account: SteamAccount,
                 avatar_manager: AvatarManager, style_manager: StyleManager):
        """
        Inicializa el widget de fila de cuenta.
        
        Args:
            parent: Widget padre
            account: Cuenta a mostrar
            avatar_manager: Gestor de avatares
            style_manager: Gestor de estilos
        """
        self.account = account
        self.avatar_manager = avatar_manager
        self.style_manager = style_manager
        
        # Callbacks para eventos
        self.on_select_origen: Optional[Callable[[SteamAccount], None]] = None
        self.on_select_destino: Optional[Callable[[SteamAccount], None]] = None
        self.on_ignore_account: Optional[Callable[[SteamAccount], None]] = None
        
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
        self.style_manager.apply_account_style(
            self.frame, "normal", self.avatar_label, self.info_label)
        
        # Botones de acción
        self.btn_origen = IconHelper.create_icon_button(
            self.frame, "origen", "Origen",
            self._on_origen_clicked
        )
        self.btn_origen.grid(row=0, column=2, padx=5)

        # Sin carpeta 570 no hay nada que copiar: la cuenta solo sirve como destino
        if not self.account.config_exists:
            self.btn_origen.config(state='disabled')

        self.btn_destino = IconHelper.create_icon_button(
            self.frame, "destino", "Destino", 
            self._on_destino_clicked
        )
        self.btn_destino.grid(row=0, column=3, padx=5)
        
        self.btn_ignorar = IconHelper.create_icon_button(
            self.frame, "ignorar", "Ignorar",
            self._on_ignorar_clicked
        )
        self.btn_ignorar.grid(row=0, column=4, padx=5)
        
        # Configurar expansión de columnas
        self.frame.columnconfigure(1, weight=1)
    
    def _on_origen_clicked(self) -> None:
        """Maneja el clic en el botón origen."""
        if self.on_select_origen:
            self.on_select_origen(self.account)
            self.log_method_call("select_origen", account=self.account.steamid)
    
    def _on_destino_clicked(self) -> None:
        """Maneja el clic en el botón destino."""
        if self.on_select_destino:
            self.on_select_destino(self.account)
            self.log_method_call("select_destino", account=self.account.steamid)
    
    def _on_ignorar_clicked(self) -> None:
        """Maneja el clic en el botón ignorar."""
        if self.on_ignore_account:
            self.on_ignore_account(self.account)
            self.log_method_call("ignore_account", account=self.account.steamid)
    
    def set_selection_state(self, selection: AppSelection) -> None:
        """
        Actualiza el estado visual basado en la selección actual.
        
        Args:
            selection: Selección actual de la aplicación
        """
        if selection.origen == self.account:
            style_type = "origen"
        elif selection.destino == self.account:
            style_type = "destino"
        else:
            style_type = "normal"
        self.style_manager.apply_account_style(
            self.frame, style_type, self.avatar_label, self.info_label)
    
    def pack(self, **kwargs) -> None:
        """Empaqueta el frame principal."""
        self.frame.pack(fill='x', padx=5, pady=3, **kwargs)
    
    def destroy(self) -> None:
        """Destruye el widget."""
        self.frame.destroy()


class PaginationControlWidget(LoggingMixin):
    """
    Widget de controles de paginación con selector de elementos por página.
    
    Combina el selector de items por página con la navegación de páginas.
    """
    
    def __init__(self, parent: tk.Widget, pagination: PaginationInfo):
        """
        Inicializa el widget de controles de paginación.
        
        Args:
            parent: Widget padre
            pagination: Información de paginación
        """
        self.pagination = pagination
        self.parent = parent
        
        # Callbacks
        self.on_items_per_page_changed: Optional[Callable[[int], None]] = None
        self.on_page_changed: Optional[Callable[[int], None]] = None
        
        # Crear frames
        self.controls_frame = ttk.Frame(parent)
        self.navigation_frame = ttk.Frame(parent)
        
        self._create_controls()
        self._create_navigation()
    
    def _create_controls(self) -> None:
        """Crea los controles superiores (items por página)."""
        label, combo = WidgetFactory.create_combo_with_label(
            self.controls_frame, 
            "Mostrar", 
            [str(x) for x in ITEMS_PER_PAGE_OPTIONS],
            icon_name="pagina",
            width=5
        )
        
        label.pack(side='left', padx=5)
        combo.pack(side='left', padx=5)
        
        # Configurar valor actual
        combo.set(str(self.pagination.items_per_page))
        combo.bind('<<ComboboxSelected>>', self._on_items_changed)
        
        self.items_combo = combo
        
        # Texto explicativo
        tk.Label(self.controls_frame, text="cuentas por página").pack(side='left', padx=5)
    
    def _create_navigation(self) -> None:
        """Crea los controles de navegación."""
        self.pagination_widget = PaginationWidget(
            self.navigation_frame,
            self.pagination,
            self._on_page_change
        )
    
    def _on_items_changed(self, event=None) -> None:
        """Maneja el cambio en items por página."""
        try:
            new_items = int(self.items_combo.get())
            if self.on_items_per_page_changed:
                self.on_items_per_page_changed(new_items)
                self.log_method_call("items_per_page_changed", items=new_items)
                
        except ValueError:
            self.logger.warning("Valor inválido para items por página")
    
    def _on_page_change(self, new_page: int) -> None:
        """Maneja el cambio de página."""
        if self.on_page_changed:
            self.on_page_changed(new_page)
    
    def update_pagination(self, pagination: PaginationInfo) -> None:
        """
        Actualiza la información de paginación y re-renderiza.
        
        Args:
            pagination: Nueva información de paginación
        """
        self.pagination = pagination
        self.pagination_widget.pagination = pagination
        self.render()
    
    def render(self) -> None:
        """Renderiza los controles."""
        # Configurar grid del parent para los frames
        self.parent.grid_rowconfigure(0, weight=0)  # Controles fijo
        self.parent.grid_rowconfigure(1, weight=0)  # Navegación fijo
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Mostrar frame de controles usando grid
        self.controls_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        
        # Renderizar navegación solo si hay múltiples páginas
        if self.pagination.total_pages > 1:
            self.navigation_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
            self.pagination_widget.render()
        else:
            self.navigation_frame.grid_remove()


class AccountListWidget(LoggingMixin):
    """
    Widget principal para mostrar la lista de cuentas con paginación.
    
    Maneja la visualización de cuentas, paginación y eventos de selección.
    """
    
    def __init__(self, parent: tk.Widget, title: str = "Cuentas Steam con Dota 2"):
        """
        Inicializa el widget de lista de cuentas.
        
        Args:
            parent: Widget padre
            title: Título de la lista
        """
        self.parent = parent
        self.title = title
        
        # Datos
        self.accounts: List[SteamAccount] = []
        self.current_accounts: List[SteamAccount] = []
        self.selection = AppSelection()
        self.pagination = PaginationInfo()
        
        # Managers
        self.avatar_manager = AvatarManager()
        self.style_manager = StyleManager(parent.winfo_toplevel())
        
        # Widgets de cuenta actuales
        self.account_widgets: List[AccountRowWidget] = []
        
        # Callbacks
        self.on_selection_changed: Optional[Callable[[AppSelection], None]] = None
        self.on_account_ignored: Optional[Callable[[SteamAccount], None]] = None
        
        # Crear interfaz
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Crea todos los widgets del componente."""
        # Configurar grid del parent
        self.parent.grid_rowconfigure(0, weight=0)  # Título fijo
        self.parent.grid_rowconfigure(1, weight=0)  # Controles paginación fijo
        self.parent.grid_rowconfigure(2, weight=1)  # Lista de cuentas expansible
        self.parent.grid_columnconfigure(0, weight=1)
        
        # Título
        title_text = IconHelper.text_with_icon("cuentas", self.title)
        self.title_label = tk.Label(
            self.parent, 
            text=title_text, 
            font=("Arial", 12, "bold")
        )
        self.title_label.grid(row=0, column=0, pady=10, sticky='ew')
        
        # Frame para controles de paginación (parte superior)
        pagination_frame = ttk.Frame(self.parent)
        pagination_frame.grid(row=1, column=0, sticky='ew', pady=(0, 5))
        
        # Controles de paginación
        self.pagination_controls = PaginationControlWidget(pagination_frame, self.pagination)
        self.pagination_controls.on_items_per_page_changed = self._on_items_per_page_changed
        self.pagination_controls.on_page_changed = self._on_page_changed
        
        # Frame con scrollbar para la lista de cuentas
        self._create_scrollable_accounts_frame()
    
    def _create_scrollable_accounts_frame(self) -> None:
        """Crea un frame scrollable para la lista de cuentas."""
        # Frame contenedor principal para la lista
        container_frame = ttk.Frame(self.parent)
        container_frame.grid(row=2, column=0, sticky='nsew', padx=5)
        container_frame.grid_rowconfigure(0, weight=1)
        container_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas para el contenido scrollable
        self.canvas = tk.Canvas(container_frame, highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky='nsew')
        
        # Scrollbar vertical
        v_scrollbar = ttk.Scrollbar(container_frame, orient='vertical', command=self.canvas.yview)
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        self.canvas.configure(yscrollcommand=v_scrollbar.set)
        
        # Frame interno para las cuentas
        self.accounts_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.accounts_frame, anchor='nw')
        
        # Configurar scroll con rueda del mouse
        self._bind_mousewheel()
        
        # Configurar resize del canvas
        self.accounts_frame.bind('<Configure>', self._on_frame_configure)
        self.canvas.bind('<Configure>', self._on_canvas_configure)
    
    def _bind_mousewheel(self) -> None:
        """Configura el scroll con la rueda del mouse."""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)
    
    def _on_frame_configure(self, event=None) -> None:
        """Actualiza el scroll region cuando cambia el frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event=None) -> None:
        """Actualiza el ancho del frame interno cuando cambia el canvas."""
        canvas_width = self.canvas.winfo_width()
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def set_accounts(self, accounts: List[SteamAccount]) -> None:
        """
        Establece la lista de cuentas a mostrar.
        
        Args:
            accounts: Lista de cuentas
        """
        self.accounts = accounts.copy()
        self.pagination.total_items = len(accounts)
        
        # Precargar avatares
        self.avatar_manager.preload_avatars(accounts)
        
        self._update_display()
        self.log_method_call("set_accounts", count=len(accounts))
    
    def set_selection(self, selection: AppSelection) -> None:
        """
        Establece la selección actual.
        
        Args:
            selection: Selección actual
        """
        self.selection = selection
        self._update_selection_styles()
    
    def _update_display(self) -> None:
        """Actualiza la visualización de cuentas."""
        # Limpiar widgets existentes
        self._clear_account_widgets()
        
        # Obtener cuentas de la página actual
        self.current_accounts = self.pagination.get_page_items(self.accounts)
        
        # Crear widgets para cuentas actuales
        for account in self.current_accounts:
            widget = self._create_account_widget(account)
            self.account_widgets.append(widget)
        
        # Actualizar controles de paginación
        self.pagination_controls.update_pagination(self.pagination)
        self.pagination_controls.render()
    
    def _create_account_widget(self, account: SteamAccount) -> AccountRowWidget:
        """Crea un widget para una cuenta específica."""
        widget = AccountRowWidget(
            self.accounts_frame, 
            account, 
            self.avatar_manager,
            self.style_manager
        )
        
        # Configurar callbacks
        widget.on_select_origen = self._on_select_origen
        widget.on_select_destino = self._on_select_destino
        widget.on_ignore_account = self._on_ignore_account
        
        # Aplicar estado de selección
        widget.set_selection_state(self.selection)
        
        # Mostrar widget
        widget.pack()
        
        return widget
    
    def _clear_account_widgets(self) -> None:
        """Limpia todos los widgets de cuenta."""
        for widget in self.account_widgets:
            widget.destroy()
        self.account_widgets.clear()
    
    def _update_selection_styles(self) -> None:
        """Actualiza los estilos basados en la selección actual."""
        for widget in self.account_widgets:
            widget.set_selection_state(self.selection)
    
    def _on_select_origen(self, account: SteamAccount) -> None:
        """Maneja la selección de cuenta origen."""
        self.selection.set_origen(account)
        self._update_selection_styles()
        
        if self.on_selection_changed:
            self.on_selection_changed(self.selection)
    
    def _on_select_destino(self, account: SteamAccount) -> None:
        """Maneja la selección de cuenta destino."""
        self.selection.set_destino(account)
        self._update_selection_styles()
        
        if self.on_selection_changed:
            self.on_selection_changed(self.selection)
    
    def _on_ignore_account(self, account: SteamAccount) -> None:
        """Maneja la solicitud de ignorar cuenta."""
        if self.on_account_ignored:
            self.on_account_ignored(account)
    
    def _on_items_per_page_changed(self, new_items: int) -> None:
        """Maneja el cambio en items por página."""
        self.pagination.items_per_page = new_items
        self.pagination.set_page(1)  # Volver a primera página
        self._update_display()
    
    def _on_page_changed(self, new_page: int) -> None:
        """Maneja el cambio de página."""
        self.pagination.set_page(new_page)
        self._update_display()
    
    def navigate_to_account(self, account: SteamAccount) -> bool:
        """
        Navega a la página que contiene una cuenta específica.
        
        Args:
            account: Cuenta a buscar
            
        Returns:
            True si se encontró la cuenta
        """
        try:
            account_page = self.pagination.find_item_page(self.accounts, account)
            self.pagination.set_page(account_page)
            self._update_display()
            return True
            
        except ValueError:
            self.logger.warning(f"Cuenta no encontrada: {account.steamid}")
            return False


class StatusWidget(LoggingMixin):
    """
    Widget para mostrar el estado actual de la selección.
    
    Muestra información sobre la selección actual y validaciones.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Inicializa el widget de estado.
        
        Args:
            parent: Widget padre
        """
        self.parent = parent
        
        # Estado actual
        self.selection = AppSelection()
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Crea los widgets del estado."""
        # Frame contenedor para el estado
        self.status_frame = ttk.Frame(self.parent)
        
        # Separador visual
        separator = ttk.Separator(self.status_frame, orient='horizontal')
        separator.pack(fill='x', pady=(0, 5))
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Selecciona origen y destino",
            font=("Arial", 11, "bold"),
            fg=palette()["status_info"]
        )
        self.status_label.pack(pady=5)
    
    def position_fixed(self, row: int, column: int) -> None:
        """Posiciona el widget en una posición fija usando grid."""
        self.status_frame.grid(row=row, column=column, sticky='ew', pady=5)
    
    def update_status(self, selection: AppSelection) -> None:
        """
        Actualiza el estado mostrado.
        
        Args:
            selection: Selección actual
        """
        self.selection = selection
        
        # Determinar mensaje y color
        message = selection.copy_description
        
        colors = palette()
        if not selection.is_complete:
            color = colors["status_info"]
        elif not selection.is_valid:
            color = colors["status_error"]
        else:
            color = colors["status_ok"]
        
        # Actualizar label
        self.status_label.config(text=message, fg=color)
        self.log_method_call("update_status", message=message)


class ActionButtonsWidget(LoggingMixin):
    """
    Widget para los botones de acción principales.
    
    Maneja los botones de copiar y cancelar selección.
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Inicializa el widget de botones de acción.
        
        Args:
            parent: Widget padre
        """
        self.parent = parent
        self.selection = AppSelection()
        
        # Callbacks
        self.on_copy_clicked: Optional[Callable[[], None]] = None
        self.on_cancel_clicked: Optional[Callable[[], None]] = None
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Crea los botones de acción."""
        # Frame contenedor para los botones
        self.buttons_container = ttk.Frame(self.parent)
        
        # Frame para centrar los botones
        buttons_frame = ttk.Frame(self.buttons_container)
        buttons_frame.pack(pady=10)
        
        # Botón cancelar
        self.btn_cancelar = IconHelper.create_icon_button(
            buttons_frame, "cancelar", "Cancelar selección",
            self._on_cancel_clicked
        )
        self.btn_cancelar.pack(side='left', padx=10)
        
        # Botón copiar
        self.btn_copiar = IconHelper.create_icon_button(
            buttons_frame, "copiar", "Copiar configuración",
            self._on_copy_clicked,
            state='disabled'
        )
        self.btn_copiar.pack(side='left', padx=10)
    
    def position_fixed(self, row: int, column: int) -> None:
        """Posiciona el widget en una posición fija usando grid."""
        self.buttons_container.grid(row=row, column=column, sticky='ew', pady=5)
    
    def update_selection(self, selection: AppSelection) -> None:
        """
        Actualiza los botones basado en la selección.
        
        Args:
            selection: Selección actual
        """
        self.selection = selection
        
        # Habilitar/deshabilitar botón copiar
        if selection.is_valid:
            self.btn_copiar.config(state='normal')
        else:
            self.btn_copiar.config(state='disabled')
    
    def _on_copy_clicked(self) -> None:
        """Maneja el clic en copiar."""
        if self.on_copy_clicked:
            self.on_copy_clicked()
            self.log_method_call("copy_clicked")
    
    def _on_cancel_clicked(self) -> None:
        """Maneja el clic en cancelar."""
        if self.on_cancel_clicked:
            self.on_cancel_clicked()
            self.log_method_call("cancel_clicked")
