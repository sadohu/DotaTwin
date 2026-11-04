"""
Temas visuales de DotaTwin (oscuro y claro).

La interfaz mezcla widgets ``tk`` y ``ttk``: los ``ttk`` se pintan con
``ttk.Style`` y los ``tk`` con la base de opciones de Tk, que solo afecta a
los widgets creados después. Por eso cambiar de tema reconstruye la interfaz.

Colores con significado, iguales en los dos temas:
- Azul: origen (la cuenta que ya tiene la configuración)
- Verde: destino (la cuenta que la recibe) y la acción principal, copiar
- Rojo: borrar o cancelar (limpiar la selección)
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict

DEFAULT_THEME = "oscuro"

FONT_FAMILY = "Segoe UI"
FONTS = {
    "title": (FONT_FAMILY, 13, "bold"),
    "name": (FONT_FAMILY, 10, "bold"),
    "small": (FONT_FAMILY, 9),
    "badge": (FONT_FAMILY, 8, "bold"),
    "step": (FONT_FAMILY, 10),
    "chip_label": (FONT_FAMILY, 8, "bold"),
    "chip": (FONT_FAMILY, 11, "bold"),
    "button": (FONT_FAMILY, 9),
    "button_bold": (FONT_FAMILY, 9, "bold"),
    "primary": (FONT_FAMILY, 11, "bold"),
    "dialog_title": (FONT_FAMILY, 12, "bold"),
    "dialog": (FONT_FAMILY, 10),
}

THEMES: Dict[str, Dict[str, str]] = {
    "oscuro": {
        "bg": "#1e1f22",            # Fondo de ventana
        "surface": "#2b2d31",       # Filas de cuentas y tarjetas
        "fg": "#e6e6e6",            # Texto principal
        "muted": "#9a9ca3",         # Texto secundario
        "button": "#3a3d43",
        "button_hover": "#4a4e55",
        "button_pressed": "#2f3237",
        "border": "#44474e",
        "input": "#26282c",
        "select": "#3d6fb4",
        "select_fg": "#ffffff",
        "origen": "#1f3b57",        # Fila origen
        "destino": "#1e4430",       # Fila destino
        "ignorada": "#4a2426",
        "origen_strong": "#2f6fd1", # Botón / insignia origen
        "origen_hover": "#4182e6",
        "destino_strong": "#2e9a57",
        "destino_hover": "#38b366",
        "copy": "#2e9a57",          # Botón copiar
        "copy_hover": "#38b366",
        "copy_pressed": "#26824a",
        "danger": "#c23c2a",        # Botón limpiar selección
        "danger_hover": "#d94b37",
        "danger_pressed": "#a83224",
        "warning": "#d29922",       # Avisos
        "on_strong": "#ffffff",     # Texto sobre botones de color
        "selected_page": "#3d6fb4",
        "status_info": "#6cb6ff",
        "status_error": "#ff7b72",
        "status_ok": "#56d364",
        "link": "#6cb6ff",
        "accent": "#9cc4ff",
    },
    "claro": {
        "bg": "#f3f4f6",
        "surface": "#ffffff",
        "fg": "#1f2328",
        "muted": "#6b7280",
        "button": "#e5e7eb",
        "button_hover": "#d9dce1",
        "button_pressed": "#cfd3d9",
        "border": "#d0d4da",
        "input": "#ffffff",
        "select": "#1f6fd1",
        "select_fg": "#ffffff",
        "origen": "#dbeafe",
        "destino": "#dcfce7",
        "ignorada": "#fee2e2",
        "origen_strong": "#1f6fd1",
        "origen_hover": "#3580e0",
        "destino_strong": "#1f8a4c",
        "destino_hover": "#26a159",
        "copy": "#1f8a4c",
        "copy_hover": "#26a159",
        "copy_pressed": "#19733f",
        "danger": "#c23c2a",
        "danger_hover": "#d94b37",
        "danger_pressed": "#a83224",
        "warning": "#b7791f",
        "on_strong": "#ffffff",
        "selected_page": "#1f6fd1",
        "status_info": "#1f6fd1",
        "status_error": "#c0392b",
        "status_ok": "#1f8a4c",
        "link": "#1f6fd1",
        "accent": "#174ea6",
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

    style = ttk.Style(root)
    # 'clam' es el tema de ttk que admite colores personalizados en botones
    style.theme_use("clam")
    _configure_styles(style, colors)
    _configure_tk_options(root, colors)
    root.configure(background=colors["bg"])
    apply_title_bar(root)


def _configure_styles(style: ttk.Style, c: Dict[str, str]) -> None:
    """Colores y estilos de los widgets ttk."""
    style.configure(".", background=c["bg"], foreground=c["fg"],
                    fieldbackground=c["input"], bordercolor=c["border"],
                    darkcolor=c["bg"], lightcolor=c["bg"], troughcolor=c["bg"],
                    selectbackground=c["select"], selectforeground=c["select_fg"],
                    insertcolor=c["fg"], focuscolor=c["border"], font=FONTS["button"])
    style.map(".", foreground=[("disabled", c["muted"])])

    # Botón neutro (Ignorar, Restaurar, Limpiar, paginación)
    _button_style(style, "TButton", c["button"], c["button_hover"],
                  c["button_pressed"], c["fg"], c)
    # Botones con significado
    _button_style(style, "Origen.TButton", c["origen_strong"], c["origen_hover"],
                  c["origen_strong"], c["on_strong"], c, font=FONTS["button_bold"])
    _button_style(style, "Destino.TButton", c["destino_strong"], c["destino_hover"],
                  c["destino_strong"], c["on_strong"], c, font=FONTS["button_bold"])
    _button_style(style, "Primary.TButton", c["copy"], c["copy_hover"],
                  c["copy_pressed"], c["on_strong"], c,
                  font=FONTS["primary"], padding=(20, 8))
    _button_style(style, "Danger.TButton", c["danger"], c["danger_hover"],
                  c["danger_pressed"], c["on_strong"], c,
                  font=FONTS["button_bold"], padding=(14, 9))
    # Confirmación genérica (Ignorar, Restaurar, Aceptar...): azul
    _button_style(style, "Accent.TButton", c["origen_strong"], c["origen_hover"],
                  c["origen_strong"], c["on_strong"], c,
                  font=FONTS["button_bold"], padding=(16, 6))
    # Confirmación de copiar/guardar en diálogos: verde, del mismo alto que Cancelar
    _button_style(style, "Success.TButton", c["copy"], c["copy_hover"],
                  c["copy_pressed"], c["on_strong"], c,
                  font=FONTS["button_bold"], padding=(16, 6))
    # Botón neutro de los diálogos, con el mismo alto que los de color
    _button_style(style, "Dialog.TButton", c["button"], c["button_hover"],
                  c["button_pressed"], c["fg"], c, padding=(16, 6))

    style.configure("TNotebook", background=c["bg"], bordercolor=c["border"],
                    lightcolor=c["bg"], darkcolor=c["bg"])
    style.configure("TNotebook.Tab", background=c["surface"], foreground=c["muted"],
                    bordercolor=c["border"], lightcolor=c["surface"],
                    darkcolor=c["surface"], padding=(14, 5))
    style.map("TNotebook.Tab",
              background=[("selected", c["bg"]), ("active", c["button_hover"])],
              lightcolor=[("selected", c["bg"])],
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

    # Filas de cuentas, tarjeta de resumen y página seleccionada
    style.configure("Origen.TFrame", background=c["origen"])
    style.configure("Destino.TFrame", background=c["destino"])
    style.configure("Normal.TFrame", background=c["surface"])
    style.configure("Ignorada.TFrame", background=c["ignorada"])
    style.configure("Card.TFrame", background=c["surface"])
    style.configure("Selected.TLabel", background=c["selected_page"], relief="raised")


def _button_style(style: ttk.Style, name: str, bg: str, hover: str, pressed: str,
                  fg: str, c: Dict[str, str], font=None, padding=(10, 4)) -> None:
    """Define un estilo de botón plano con colores de reposo, hover y pulsado."""
    style.configure(name, background=bg, foreground=fg, bordercolor=bg,
                    lightcolor=bg, darkcolor=bg, padding=padding,
                    font=font or FONTS["button"], focuscolor=bg)
    style.map(name,
              background=[("disabled", c["button"]), ("pressed", pressed), ("active", hover)],
              bordercolor=[("disabled", c["button"]), ("pressed", pressed), ("active", hover)],
              lightcolor=[("disabled", c["button"]), ("pressed", pressed), ("active", hover)],
              darkcolor=[("disabled", c["button"]), ("pressed", pressed), ("active", hover)],
              foreground=[("disabled", c["muted"])])


def _configure_tk_options(root: tk.Tk, c: Dict[str, str]) -> None:
    """Colores por defecto de los widgets tk (Label, Canvas, Text, Toplevel...)."""
    root.option_clear()
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
