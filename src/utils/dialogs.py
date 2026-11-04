"""
Diálogos y avisos con el tema de la aplicación.

Reemplazan a los ``messagebox`` de Windows, que no siguen el modo oscuro y
muestran los emojis en blanco y negro.

- ``ThemedDialog``: ventana modal con insignia de color, título, mensaje y botones.
- ``Toast``: aviso breve dentro de la ventana que desaparece solo, para
  confirmar acciones sin obligar a pulsar "Aceptar".
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional, Tuple

from .icons import get_badge
from .theme import FONTS, palette, apply_title_bar

# Tipo de diálogo -> color de su insignia
_KIND_COLORS = {
    "info": "origen_strong",
    "question": "origen_strong",
    "success": "copy",
    "warning": "warning",
    "error": "danger",
}

# (texto, valor devuelto, estilo ttk)
Button = Tuple[str, object, str]


class ThemedDialog:
    """
    Diálogo modal con el tema actual.

    Enter pulsa el botón principal (el último) y Escape el primero
    (o cierra si solo hay uno).
    """

    def __init__(self, parent: Optional[tk.Misc], title: str, message: str,
                 kind: str = "info", buttons: Optional[List[Button]] = None,
                 heading: Optional[str] = None):
        self.parent = parent or tk._default_root
        self.title = title
        self.message = message
        self.kind = kind if kind in _KIND_COLORS else "info"
        self.buttons = buttons or [("Aceptar", True, "Accent.TButton")]
        self.heading = heading
        self.result = self.buttons[0][1] if len(self.buttons) > 1 else None

    def show(self):
        """Muestra el diálogo, espera a que se cierre y devuelve el valor del botón pulsado."""
        colors = palette()
        self.window = tk.Toplevel(self.parent)
        self.window.title(self.title)
        self.window.resizable(False, False)
        self.window.configure(bg=colors["bg"])
        if self.parent and self.parent.winfo_viewable():
            self.window.transient(self.parent)
        self._set_icon()

        body = tk.Frame(self.window, bg=colors["bg"], padx=22, pady=18)
        body.pack(fill='both', expand=True)

        badge = get_badge(self.kind, colors[_KIND_COLORS[self.kind]])
        tk.Label(body, image=badge, bg=colors["bg"]).grid(row=0, column=0, rowspan=2,
                                                          sticky='n', padx=(0, 16))
        text_row = 0
        if self.heading:
            tk.Label(body, text=self.heading, font=FONTS["dialog_title"], bg=colors["bg"],
                     fg=colors["fg"], justify='left', anchor='w', wraplength=380
                     ).grid(row=0, column=1, sticky='w', pady=(0, 6))
            text_row = 1
        tk.Label(body, text=self.message, font=FONTS["dialog"], bg=colors["bg"],
                 fg=colors["fg"] if not self.heading else colors["muted"],
                 justify='left', anchor='w', wraplength=380
                 ).grid(row=text_row, column=1, sticky='w')

        footer = tk.Frame(self.window, bg=colors["surface"], padx=16, pady=12)
        footer.pack(fill='x')
        for text, value, style in reversed(self.buttons):
            ttk.Button(footer, text=text, style=style,
                       command=lambda v=value: self._close(v)).pack(side='right', padx=(8, 0))

        default_value = self.buttons[-1][1]
        cancel_value = self.buttons[0][1] if len(self.buttons) > 1 else default_value
        self.window.bind("<Return>", lambda e: self._close(default_value))
        self.window.bind("<Escape>", lambda e: self._close(cancel_value))
        self.window.protocol("WM_DELETE_WINDOW", lambda: self._close(cancel_value))

        self._center()
        apply_title_bar(self.window)
        self.window.lift()
        self.window.focus_force()
        self.window.grab_set()
        self.window.wait_window()
        return self.result

    def _close(self, value) -> None:
        self.result = value
        self.window.grab_release()
        self.window.destroy()

    def _center(self) -> None:
        """Centra el diálogo sobre la ventana principal (o en la pantalla si no está visible)."""
        self.window.update_idletasks()
        width, height = self.window.winfo_reqwidth(), self.window.winfo_reqheight()
        if self.parent and self.parent.winfo_viewable():
            x = self.parent.winfo_rootx() + (self.parent.winfo_width() - width) // 2
            y = self.parent.winfo_rooty() + (self.parent.winfo_height() - height) // 3
        else:
            x = (self.window.winfo_screenwidth() - width) // 2
            y = (self.window.winfo_screenheight() - height) // 3
        self.window.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def _set_icon(self) -> None:
        try:
            from config.settings import ICON_PATH
            self.window.iconbitmap(str(ICON_PATH))
        except Exception:
            pass


class Toast:
    """Aviso breve en la parte baja de la ventana; desaparece solo."""

    DURATION_MS = 2600
    _current: Optional[tk.Frame] = None

    @classmethod
    def show(cls, root: tk.Misc, message: str, kind: str = "success") -> None:
        colors = palette()
        if cls._current is not None and cls._current.winfo_exists():
            cls._current.destroy()

        frame = tk.Frame(root, bg=colors["surface"], highlightthickness=1,
                         highlightbackground=colors["border"], padx=12, pady=8)
        color = colors[_KIND_COLORS.get(kind, "copy")]
        tk.Label(frame, image=get_badge(kind, color, size=18),
                 bg=colors["surface"]).pack(side='left', padx=(0, 8))
        tk.Label(frame, text=message, font=FONTS["step"], bg=colors["surface"],
                 fg=colors["fg"]).pack(side='left')
        frame.place(relx=0.5, rely=1.0, anchor='s', y=-200)
        frame.lift()
        cls._current = frame
        root.after(cls.DURATION_MS, lambda: frame.winfo_exists() and frame.destroy())
