"""
Ventana "Restaurar respaldo": lista los respaldos guardados y permite
recuperar cualquiera de ellos.
"""

import os
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

from ..models.domain_models import BackupInfo, SteamAccount
from ..utils.theme import FONTS, palette, apply_title_bar
from ..utils.ui_utils import AvatarManager, Tooltip
from config.settings import MAX_BACKUPS_PER_ACCOUNT


class RestoreBackupDialog:
    """
    Lista de respaldos (del más reciente al más antiguo) con un botón
    Restaurar en cada uno. La restauración la hace ``on_restore``, que
    devuelve True si se completó, para refrescar la lista.
    """

    LIST_HEIGHT = 330

    def __init__(self, parent: tk.Tk, list_backups: Callable[[], List[BackupInfo]],
                 find_account: Callable[[str], Optional[SteamAccount]],
                 on_restore: Callable[[BackupInfo, str], bool], backup_dir):
        self.parent = parent
        self.list_backups = list_backups
        self.find_account = find_account
        self.on_restore = on_restore
        self.backup_dir = backup_dir
        self.avatar_manager = AvatarManager()

    def show(self) -> None:
        colors = palette()
        self.window = tk.Toplevel(self.parent)
        self.window.title("Restaurar respaldo")
        self.window.resizable(False, False)
        self.window.configure(bg=colors["bg"])
        self.window.transient(self.parent)
        try:
            from config.settings import ICON_PATH
            self.window.iconbitmap(str(ICON_PATH))
        except Exception:
            pass

        header = tk.Frame(self.window, bg=colors["bg"], padx=22, pady=16)
        header.pack(fill='x')
        tk.Label(header, text="Elige qué configuración recuperar", font=FONTS["dialog_title"],
                 bg=colors["bg"], fg=colors["fg"]).pack(anchor='w')
        tk.Label(header, text="Cada vez que copias, DotaTwin guarda cómo estaba la cuenta de "
                              f"destino. Se conservan los {MAX_BACKUPS_PER_ACCOUNT} más "
                              "recientes de cada cuenta.",
                 font=FONTS["dialog"], bg=colors["bg"], fg=colors["muted"],
                 justify='left', wraplength=500).pack(anchor='w', pady=(4, 0))

        # Lista con scroll
        body = tk.Frame(self.window, bg=colors["bg"], padx=22)
        body.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(body, bg=colors["bg"], highlightthickness=0,
                                width=520, height=self.LIST_HEIGHT)
        scrollbar = ttk.Scrollbar(body, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        self.rows = tk.Frame(self.canvas, bg=colors["bg"])
        # Ancho final desde el inicio para que las filas se dibujen completas a la primera
        self._rows_window = self.canvas.create_window((0, 0), window=self.rows, anchor='nw',
                                                      width=520)
        self.rows.bind('<Configure>', lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox('all')))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(
            self._rows_window, width=e.width))
        self.window.bind('<MouseWheel>', lambda e: self.canvas.yview_scroll(
            int(-e.delta / 120), 'units'))

        footer = tk.Frame(self.window, bg=colors["surface"], padx=16, pady=12)
        footer.pack(fill='x', pady=(14, 0))
        ttk.Button(footer, text="Cerrar", style="Dialog.TButton",
                   command=self.window.destroy).pack(side='right')
        open_btn = ttk.Button(footer, text="Abrir carpeta", style="Dialog.TButton",
                              command=self._open_folder)
        open_btn.pack(side='left')
        Tooltip(open_btn, "Ver los respaldos en el Explorador de Windows")

        self.window.bind("<Escape>", lambda e: self.window.destroy())
        self._fill()
        self._center()
        apply_title_bar(self.window)
        self.window.focus_force()
        self.window.grab_set()
        self.window.wait_window()

    def _fill(self) -> None:
        """(Re)crea las filas de la lista."""
        colors = palette()
        for child in self.rows.winfo_children():
            child.destroy()

        backups = self.list_backups()
        if not backups:
            tk.Label(self.rows, text="Todavía no hay respaldos.\nSe crea uno cada vez que "
                                     "copias una configuración a una cuenta.",
                     font=FONTS["step"], bg=colors["bg"], fg=colors["muted"],
                     justify='center').pack(pady=40)
            return

        for backup in backups:
            self._create_row(backup)
        self.canvas.yview_moveto(0)

    def _create_row(self, backup: BackupInfo) -> None:
        colors = palette()
        account = self.find_account(backup.steamid)
        name = account.nombre if account else "Cuenta no encontrada"
        avatar_account = account or SteamAccount(backup.steamid, name, backup.path)

        row = tk.Frame(self.rows, bg=colors["surface"], padx=10, pady=7)
        row.pack(fill='x', pady=3, padx=(0, 6))
        tk.Label(row, image=self.avatar_manager.get_avatar(avatar_account),
                 bg=colors["surface"]).grid(row=0, column=0, rowspan=2, padx=(0, 10))
        tk.Label(row, text=name, font=FONTS["name"], bg=colors["surface"],
                 fg=colors["fg"] if account else colors["muted"], anchor='w'
                 ).grid(row=0, column=1, sticky='sw')
        tk.Label(row, text=f"Respaldo del {backup.created_text}", font=FONTS["small"],
                 bg=colors["surface"], fg=colors["muted"], anchor='w'
                 ).grid(row=1, column=1, sticky='nw')
        button = ttk.Button(row, text="Restaurar", style="Accent.TButton", width=10,
                            command=lambda b=backup, n=name: self._restore(b, n))
        button.grid(row=0, column=2, rowspan=2)
        Tooltip(button, f"Volver a dejar {name} como estaba el {backup.created_text}")
        row.columnconfigure(1, weight=1)

    def _restore(self, backup: BackupInfo, name: str) -> None:
        restored = self.on_restore(backup, name)
        # Los diálogos de confirmación toman el foco modal; recuperarlo
        if self.window.winfo_exists():
            self.window.grab_set()
            if restored:
                self._fill()  # aparece el respaldo del estado anterior

    def _open_folder(self) -> None:
        try:
            os.makedirs(self.backup_dir, exist_ok=True)
            os.startfile(str(self.backup_dir))
        except OSError:
            pass

    def _center(self) -> None:
        self.window.update_idletasks()
        width, height = self.window.winfo_reqwidth(), self.window.winfo_reqheight()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() - width) // 2
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() - height) // 3
        self.window.geometry(f"+{max(x, 0)}+{max(y, 0)}")
