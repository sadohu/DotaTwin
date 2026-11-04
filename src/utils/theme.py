"""
Temas visuales de DotaTwin (oscuro y claro).

La interfaz mezcla widgets ``tk`` y ``ttk``: los ``ttk`` se pintan con
``ttk.Style`` y los ``tk`` con la base de opciones de Tk, que solo afecta a
los widgets creados después. Por eso cambiar de tema reconstruye la interfaz.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict

DEFAULT_THEME = "oscuro"

THEMES: Dict[str, Dict[str, str]] = {
    "oscuro": {
        "bg": "#1e1f22",            # Fondo de ventana
        "surface": "#2b2d31",       # Filas de cuentas
        "fg": "#e6e6e6",            # Texto principal
        "muted": "#9a9ca3",         # Texto secundario
        "button": "#3a3d43",
        "button_hover": "#4a4e55",
        "button_pressed": "#2f3237",
        "border": "#44474e",
        "input": "#26282c",
        "select": "#3d6fb4",
        "select_fg": "#ffffff",
        "origen": "#1f3b57",        # Azul oscuro
        "destino": "#1e4430",       # Verde oscuro
        "ignorada": "#4a2426",      # Rojo oscuro
        "selected_page": "#3d6fb4",
        "status_info": "#6cb6ff",
        "status_error": "#ff7b72",
        "status_ok": "#56d364",
        "link": "#6cb6ff",
        "accent": "#9cc4ff",
    },
    "claro": {
        "bg": "#f0f0f0",
        "surface": "#f0f0f0",
        "fg": "#000000",
        "muted": "gray",
        "button": "#e1e1e1",
        "button_hover": "#e5f1fb",
        "button_pressed": "#cce4f7",
        "border": "#adadad",
        "input": "#ffffff",
        "select": "#0078d7",
        "select_fg": "#ffffff",
        "origen": "#d0f0ff",        # Azul claro
        "destino": "#e0ffe0",       # Verde claro
        "ignorada": "#ffcccc",      # Rojo claro
        "selected_page": "lightblue",
        "status_info": "blue",
        "status_error": "red",
        "status_ok": "green",
        "link": "blue",
        "accent": "darkblue",
    },
}

_current_theme = DEFAULT_THEME


def normalize_theme(name: str) -> str:
    """Devuelve un nombre de tema válido (el por defecto si no existe)."""
    return name if name in THEMES else DEFAULT_THEME


def current_theme() -> str:
    """Nombre del tema activo."""
    return _current_theme


def palette() -> Dict[str, str]:
    """Colores del tema activo."""
    return THEMES[_current_theme]


def apply_theme(root: tk.Tk, name: str) -> None:
    """
    Activa un tema en toda la aplicación.

    Afecta a todos los estilos ``ttk`` al instante y a los widgets ``tk``
    que se creen a partir de ahora.
    """
    global _current_theme
    _current_theme = normalize_theme(name)
    colors = palette()
    dark = _current_theme == "oscuro"

    style = ttk.Style(root)
    # 'clam' admite colores personalizados; 'vista' es el aspecto nativo de Windows
    base = "clam" if dark or "vista" not in style.theme_names() else "vista"
    style.theme_use(base)

    if dark:
        _configure_dark_styles(style, colors)

    # Filas de cuentas y página seleccionada
    style.configure("Origen.TFrame", background=colors["origen"])
    style.configure("Destino.TFrame", background=colors["destino"])
    style.configure("Normal.TFrame", background=colors["surface"])
    style.configure("Ignorada.TFrame", background=colors["ignorada"])
    style.configure("Selected.TLabel", background=colors["selected_page"], relief="raised")

    _configure_tk_options(root, colors, dark)
    root.configure(background=colors["bg"])
    apply_title_bar(root)


def _configure_dark_styles(style: ttk.Style, c: Dict[str, str]) -> None:
    """Colores de los widgets ttk en modo oscuro."""
    style.configure(".", background=c["bg"], foreground=c["fg"],
                    fieldbackground=c["input"], bordercolor=c["border"],
                    darkcolor=c["bg"], lightcolor=c["bg"], troughcolor=c["bg"],
                    selectbackground=c["select"], selectforeground=c["select_fg"],
                    insertcolor=c["fg"], focuscolor=c["border"])
    style.map(".", foreground=[("disabled", c["muted"])])

    style.configure("TButton", background=c["button"], foreground=c["fg"],
                    bordercolor=c["border"], lightcolor=c["button"],
                    darkcolor=c["button"], padding=(8, 3))
    style.map("TButton",
              background=[("disabled", c["surface"]), ("pressed", c["button_pressed"]),
                          ("active", c["button_hover"])],
              lightcolor=[("pressed", c["button_pressed"]), ("active", c["button_hover"])],
              darkcolor=[("pressed", c["button_pressed"]), ("active", c["button_hover"])],
              foreground=[("disabled", c["muted"])])

    style.configure("TNotebook", background=c["bg"], bordercolor=c["border"],
                    lightcolor=c["bg"], darkcolor=c["bg"])
    style.configure("TNotebook.Tab", background=c["surface"], foreground=c["muted"],
                    bordercolor=c["border"], lightcolor=c["surface"],
                    darkcolor=c["surface"], padding=(12, 4))
    style.map("TNotebook.Tab",
              background=[("selected", c["button"]), ("active", c["button_hover"])],
              lightcolor=[("selected", c["button"])],
              foreground=[("selected", c["fg"]), ("active", c["fg"])])

    style.configure("TCombobox", fieldbackground=c["input"], background=c["button"],
                    foreground=c["fg"], arrowcolor=c["fg"], bordercolor=c["border"],
                    lightcolor=c["input"], darkcolor=c["input"])
    style.map("TCombobox",
              fieldbackground=[("readonly", c["input"])],
              selectbackground=[("readonly", c["input"])],
              selectforeground=[("readonly", c["fg"])],
              background=[("active", c["button_hover"])])

    style.configure("TScrollbar", background=c["button"], troughcolor=c["bg"],
                    bordercolor=c["bg"], arrowcolor=c["fg"],
                    lightcolor=c["button"], darkcolor=c["button"])
    style.map("TScrollbar", background=[("active", c["button_hover"])])

    style.configure("TSeparator", background=c["border"])


def _configure_tk_options(root: tk.Tk, c: Dict[str, str], dark: bool) -> None:
    """Colores por defecto de los widgets tk (Label, Canvas, Text, Toplevel...)."""
    root.option_clear()
    if not dark:
        return  # Modo claro: colores nativos de Windows, como antes

    options = {
        "*Background": c["bg"],
        "*Foreground": c["fg"],
        "*activeBackground": c["button_hover"],
        "*activeForeground": c["fg"],
        "*selectBackground": c["select"],
        "*selectForeground": c["select_fg"],
        "*insertBackground": c["fg"],
        "*highlightBackground": c["bg"],
        "*highlightColor": c["border"],
        "*disabledForeground": c["muted"],
        "*Text.Background": c["input"],
        "*Entry.Background": c["input"],
        "*Button.Background": c["button"],
        "*TCombobox*Listbox.background": c["input"],
        "*TCombobox*Listbox.foreground": c["fg"],
        "*TCombobox*Listbox.selectBackground": c["select"],
        "*TCombobox*Listbox.selectForeground": c["select_fg"],
    }
    for pattern, value in options.items():
        root.option_add(pattern, value)


def apply_title_bar(window: tk.Misc) -> None:
    """Pone la barra de título de Windows en oscuro o claro según el tema."""
    try:
        import ctypes

        window.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(window.winfo_id())
        value = ctypes.c_int(1 if _current_theme == "oscuro" else 0)
        # DWMWA_USE_IMMERSIVE_DARK_MODE: 20 en Windows 10 20H1+ y 11, 19 en builds anteriores
        for attribute in (20, 19):
            result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, attribute, ctypes.byref(value), ctypes.sizeof(value))
            if result == 0:
                break
    except Exception:
        pass  # No es Windows o la versión no lo soporta
