"""
Common UI components for Phyton / VT-Solutions desktop apps.

This module is intentionally lightweight and Tkinter-based.
Use it as the shared design foundation for new apps.

Recommended usage:

    from components.common_ui import Theme, create_main_window, VTHeader, VTFooter, VTButton

"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
import tkinter as tk
from tkinter import ttk


@dataclass(frozen=True)
class Theme:
    colors: dict
    typography: dict
    spacing: dict
    radius: dict
    layout: dict
    brand: dict

    @classmethod
    def from_json(cls, path: str | Path) -> "Theme":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            colors=data["colors"],
            typography=data["typography"],
            spacing=data["spacing"],
            radius=data["radius"],
            layout=data["layout"],
            brand=data["brand"],
        )


def apply_theme(root: tk.Tk, theme: Theme) -> None:
    root.configure(bg=theme.colors["app_background"])

    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure(
        "VT.TFrame",
        background=theme.colors["app_background"],
    )
    style.configure(
        "VTHeader.TFrame",
        background=theme.colors["header_background"],
    )
    style.configure(
        "VTFooter.TFrame",
        background=theme.colors["footer_background"],
    )
    style.configure(
        "VT.TLabel",
        background=theme.colors["app_background"],
        foreground=theme.colors["text_primary"],
        font=(theme.typography["font_family"], theme.typography["body_size"]),
    )


def create_main_window(
    title: str,
    theme: Theme,
    app_icon: str | None = None,
) -> tk.Tk:
    root = tk.Tk()
    root.title(title)

    width = theme.layout["default_window_width"]
    height = theme.layout["default_window_height"]
    min_width = theme.layout["min_window_width"]
    min_height = theme.layout["min_window_height"]

    root.geometry(f"{width}x{height}")
    root.minsize(min_width, min_height)

    if app_icon:
        try:
            root.iconbitmap(app_icon)
        except Exception:
            pass

    apply_theme(root, theme)
    return root


class VTHeader(tk.Frame):
    def __init__(
        self,
        master: tk.Misc,
        theme: Theme,
        app_title: str,
        subtitle: str,
        logo_text: str = "vt-solutions",
        show_theme_buttons: bool = True,
        show_help_button: bool = True,
        help_command=None,
    ):
        super().__init__(
            master,
            bg=theme.colors["header_background"],
            height=theme.layout["header_height"],
        )
        self.theme = theme
        self.pack_propagate(False)

        self.grid_columnconfigure(0, minsize=300)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, minsize=430)

        logo = tk.Label(
            self,
            text=logo_text,
            bg=theme.colors["header_background"],
            fg=theme.colors["text_primary"],
            font=(theme.typography["font_family"], 28),
            anchor="w",
        )
        logo.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(44, 20), pady=28)

        title_label = tk.Label(
            self,
            text=app_title,
            bg=theme.colors["header_background"],
            fg=theme.colors["text_primary"],
            font=(theme.typography["font_family"], theme.typography["title_size"], "bold"),
            anchor="w",
            justify="left",
            wraplength=520,
        )
        title_label.grid(row=0, column=1, sticky="ew", padx=(0, 20), pady=(28, 0))

        subtitle_label = tk.Label(
            self,
            text=subtitle,
            bg=theme.colors["header_background"],
            fg=theme.colors["text_secondary"],
            font=(theme.typography["font_family"], theme.typography["subtitle_size"]),
            anchor="w",
            justify="left",
            wraplength=620,
        )
        subtitle_label.grid(row=1, column=1, sticky="ew", padx=(0, 20), pady=(4, 28))

        actions = tk.Frame(self, bg=theme.colors["header_background"])
        actions.grid(row=0, column=2, rowspan=2, sticky="e", padx=(0, 36), pady=34)

        if show_theme_buttons:
            VTButton(actions, theme, "☀  Hellmodus", variant="secondary").pack(side="left", padx=(0, 8))
            VTButton(actions, theme, "☾  Dunkelmodus", variant="primary").pack(side="left", padx=(0, 16))

        if show_help_button:
            VTButton(actions, theme, "?  Hilfe", variant="secondary", command=help_command).pack(side="left")


class VTFooter(tk.Frame):
    def __init__(self, master: tk.Misc, theme: Theme, version: str = "1.0.0"):
        super().__init__(
            master,
            bg=theme.colors["footer_background"],
            height=theme.layout["footer_height"],
        )
        self.pack_propagate(False)

        footer_text = (
            f'{theme.brand["company"]}  |  '
            f'{theme.brand["support_email"]}  |  '
            f'{theme.brand["website"]}  |  '
            f'Version {version}'
        )

        tk.Label(
            self,
            text=footer_text,
            bg=theme.colors["footer_background"],
            fg=theme.colors["text_secondary"],
            font=(theme.typography["font_family"], theme.typography["footer_size"]),
        ).pack(expand=True)


class VTButton(tk.Button):
    VARIANTS = {
        "primary": ("primary", "primary_hover"),
        "success": ("success", "success_hover"),
        "secondary": ("secondary", "secondary_hover"),
        "danger": ("danger", "danger_hover"),
    }

    def __init__(
        self,
        master: tk.Misc,
        theme: Theme,
        text: str,
        variant: str = "primary",
        command=None,
        min_width: int = 16,
    ):
        bg_key, hover_key = self.VARIANTS.get(variant, self.VARIANTS["primary"])

        super().__init__(
            master,
            text=text,
            command=command,
            bg=theme.colors[bg_key],
            fg=theme.colors["text_primary"],
            activebackground=theme.colors[hover_key],
            activeforeground=theme.colors["text_primary"],
            relief="flat",
            bd=0,
            padx=theme.spacing["button_padding_x"],
            pady=theme.spacing["button_padding_y"],
            font=(theme.typography["font_family"], theme.typography["button_size"], "bold"),
            cursor="hand2",
            width=min_width,
        )

        self.default_bg = theme.colors[bg_key]
        self.hover_bg = theme.colors[hover_key]
        self.bind("<Enter>", lambda _event: self.configure(bg=self.hover_bg))
        self.bind("<Leave>", lambda _event: self.configure(bg=self.default_bg))


class VTPanel(tk.Frame):
    def __init__(self, master: tk.Misc, theme: Theme, border: bool = True):
        super().__init__(
            master,
            bg=theme.colors["panel_background"],
            highlightbackground=theme.colors["border"] if border else theme.colors["panel_background"],
            highlightcolor=theme.colors["border"] if border else theme.colors["panel_background"],
            highlightthickness=2 if border else 0,
            bd=0,
        )


class VTDropZone(VTPanel):
    def __init__(self, master: tk.Misc, theme: Theme, text: str = "📁  Datei hier ablegen  –  oder Schaltfläche nutzen"):
        super().__init__(master, theme, border=True)

        label = tk.Label(
            self,
            text=text,
            bg=theme.colors["panel_background"],
            fg=theme.colors["text_secondary"],
            font=(theme.typography["font_family"], theme.typography["body_size"]),
            anchor="w",
        )
        label.pack(fill="both", expand=True, padx=24, pady=22)


class VTTextPanel(VTPanel):
    def __init__(self, master: tk.Misc, theme: Theme, placeholder: str = "Hier erscheint der erkannte Text ..."):
        super().__init__(master, theme, border=True)

        self.text = tk.Text(
            self,
            bg=theme.colors["panel_background"],
            fg=theme.colors["text_primary"],
            insertbackground=theme.colors["text_primary"],
            relief="flat",
            bd=0,
            wrap="word",
            font=(theme.typography["font_family"], theme.typography["body_size"]),
        )
        self.text.pack(fill="both", expand=True, padx=18, pady=18)
        self.text.insert("1.0", placeholder)


def create_standard_layout(
    root: tk.Tk,
    theme: Theme,
    app_title: str,
    subtitle: str,
    version: str = "1.0.0",
):
    header = VTHeader(root, theme, app_title=app_title, subtitle=subtitle)
    header.pack(fill="x")

    main = tk.Frame(root, bg=theme.colors["app_background"])
    main.pack(fill="both", expand=True, padx=theme.spacing["window_padding"], pady=theme.spacing["window_padding"])

    footer = VTFooter(root, theme, version=version)
    footer.pack(fill="x", side="bottom")

    return header, main, footer
