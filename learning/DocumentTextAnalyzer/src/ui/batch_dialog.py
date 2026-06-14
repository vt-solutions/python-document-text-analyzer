"""
batch_dialog.py
PRO-Feature: Dialog fuer Batch-Verarbeitung mehrerer Dateien.
"""

import os
import sys
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES

from src.file_router import ALL_SUPPORTED_EXTS
from src.pro_batch import process_batch, combine_results
from src.theme import (
    FONT_FAMILY as FONT,
    FONT_TITLE, FONT_SECTION, FONT_LABEL, FONT_BODY,
    FONT_BUTTON, FONT_SUBTITLE, FONT_FOOTER,
    HEIGHT_BUTTON,
    NAVY_DARK, NAVY_MED, BLUE_ACCENT, WHITE,
    LIGHT_BG, LIGHT_CARD, DARK_BG, DARK_CARD,
    SEP_DARK, SUCCESS, ERROR_RED,
)
from src.version import APP_NAME, APP_VERSION, ICON_PATH


class BatchDialog(tk.Toplevel):
    """
    Batch-Verarbeitungs-Dialog (PRO).
    Nach Schließen: self.result enthält kombinierten Text oder None.
    """

    def __init__(self, parent, allow_pro: bool = True):
        super().__init__(parent)
        self.result: str | None = None
        self._allow_pro = allow_pro
        self._files: list[str] = []
        self._results: dict[str, str] = {}
        self._is_dark = ctk.get_appearance_mode() == "Dark"

        self.title(f"Batch-Verarbeitung  –  {APP_NAME}  [PRO]")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        bg = DARK_BG if self._is_dark else LIGHT_BG
        self.configure(bg=bg)

        _base = (sys._MEIPASS if hasattr(sys, "_MEIPASS")
                 else os.path.normpath(
                     os.path.join(os.path.dirname(__file__), "..", "..")))
        ico = os.path.join(_base, ICON_PATH)
        if os.path.isfile(ico):
            try:
                self.iconbitmap(ico)
            except Exception:
                pass

        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        dw, dh = min(1200, sw - 40), min(820, sh - 60)
        self.geometry(f"{dw}x{dh}+{(sw-dw)//2}+{(sh-dh)//2}")
        self.minsize(780, 560)

        self._build_ui()
        self.after(100, self._make_modal)

    def _make_modal(self):
        try:
            self.grab_set()
            self.focus_force()
            self.lift()
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  UI                                                                 #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        dark = self._is_dark
        bg   = DARK_BG if dark else LIGHT_BG

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(2, weight=0)  # Footer

        # ── Header ───────────────────────────────────────────────────
        hdr = tk.Frame(self, bg=NAVY_DARK)
        hdr.grid(row=0, column=0, sticky="ew")

        tk.Label(hdr, text="📦  Batch-Verarbeitung  [PRO]",
                 font=(FONT, FONT_SECTION, "bold"),
                 fg=WHITE, bg=NAVY_DARK, anchor="w",
                 ).pack(side="left", padx=28, pady=14)

        tk.Label(hdr, text="Mehrere Dateien auf einmal verarbeiten",
                 font=(FONT, FONT_SUBTITLE),
                 fg="#6b8caa", bg=NAVY_DARK, anchor="w",
                 ).pack(side="left", padx=(0, 28), pady=14)

        tk.Frame(self, bg=SEP_DARK, height=1).grid(row=0, column=0, sticky="sew")

        # ── Content ──────────────────────────────────────────────────
        content = ctk.CTkFrame(self, fg_color=(LIGHT_BG, DARK_BG), corner_radius=0)
        content.grid(row=1, column=0, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        self._build_left(content, dark)
        self._build_right(content, dark)

        # ── Footer ───────────────────────────────────────────────────
        foot = tk.Frame(self, bg=NAVY_DARK)
        foot.grid(row=2, column=0, sticky="ew")

        tk.Label(foot,
                 text=f"VT Document Text Converter  ·  Version {APP_VERSION}  ·  PRO-Edition",
                 font=(FONT, FONT_FOOTER), fg="#4a6a8a", bg=NAVY_DARK,
                 ).pack(side="left", padx=28, pady=8)

    def _build_left(self, parent, dark):
        """Linke Spalte: Dateiliste + Steuerung."""
        card_bg = DARK_CARD if dark else LIGHT_CARD
        txt     = WHITE if dark else NAVY_DARK

        left = ctk.CTkFrame(parent, fg_color=(LIGHT_CARD, DARK_CARD), corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)

        # Titel
        ctk.CTkLabel(left, text="Dateien",
                     font=ctk.CTkFont(family=FONT, size=FONT_LABEL, weight="bold"),
                     text_color=(NAVY_DARK, WHITE),
                     ).grid(row=0, column=0, padx=14, pady=(12, 6), sticky="w")

        # Dateiliste
        self._listbox = tk.Listbox(
            left,
            selectmode="extended",
            bg=DARK_CARD if dark else "#f0f4f8",
            fg=WHITE if dark else NAVY_DARK,
            selectbackground=BLUE_ACCENT,
            selectforeground=WHITE,
            font=(FONT, FONT_BODY),
            relief="flat",
            bd=0,
            activestyle="none",
        )
        self._listbox.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 8))

        # Scrollbar
        sb = tk.Scrollbar(left, command=self._listbox.yview)
        sb.grid(row=1, column=1, sticky="ns", pady=(0, 8))
        self._listbox.config(yscrollcommand=sb.set)

        # Drag & Drop auf Listbox
        try:
            self._listbox.drop_target_register(DND_FILES)
            self._listbox.dnd_bind("<<Drop>>", self._on_drop)
        except Exception:
            pass

        # Button-Leiste
        btn_bar = ctk.CTkFrame(left, fg_color="transparent")
        btn_bar.grid(row=2, column=0, columnspan=2, padx=14, pady=(0, 12), sticky="ew")
        btn_bar.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(btn_bar, text="+ Hinzufügen",
                      height=32, font=ctk.CTkFont(family=FONT, size=FONT_BUTTON),
                      fg_color=BLUE_ACCENT, hover_color=NAVY_MED,
                      corner_radius=6, command=self._add_files,
                      ).grid(row=0, column=0, padx=(0, 4), sticky="ew")

        ctk.CTkButton(btn_bar, text="− Entfernen",
                      height=32, font=ctk.CTkFont(family=FONT, size=FONT_BUTTON),
                      fg_color=("#6b7c93", "#3a4a5a"), hover_color=NAVY_MED,
                      corner_radius=6, command=self._remove_selected,
                      ).grid(row=0, column=1, padx=(0, 4), sticky="ew")

        ctk.CTkButton(btn_bar, text="Leeren",
                      height=32, font=ctk.CTkFont(family=FONT, size=FONT_BUTTON),
                      fg_color="#b91c1c", hover_color="#991818",
                      corner_radius=6, command=self._clear_list,
                      ).grid(row=0, column=2, sticky="ew")

        # Zähler
        self._lbl_count = ctk.CTkLabel(left, text="0 Dateien ausgewählt",
                                        font=ctk.CTkFont(family=FONT, size=FONT_FOOTER),
                                        text_color=(NAVY_DARK, "#6b8caa"))
        self._lbl_count.grid(row=3, column=0, columnspan=2, padx=14, pady=(0, 8), sticky="w")

    def _build_right(self, parent, dark):
        """Rechte Spalte: Fortschritt + Starten + Ergebnis-Vorschau."""
        right = ctk.CTkFrame(parent, fg_color=(LIGHT_BG, DARK_BG), corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=16)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)

        # Status
        self._lbl_status = ctk.CTkLabel(
            right, text="Dateien hinzufügen und Verarbeitung starten.",
            font=ctk.CTkFont(family=FONT, size=FONT_BODY),
            text_color=(NAVY_DARK, WHITE), anchor="w", wraplength=500,
        )
        self._lbl_status.grid(row=0, column=0, padx=14, pady=(12, 6), sticky="ew")

        # Fortschrittsbalken
        self._progress = ctk.CTkProgressBar(
            right, mode="determinate",
            fg_color=("#dce3ec", "#1e3a5a"),
            progress_color=BLUE_ACCENT,
        )
        self._progress.set(0)
        self._progress.grid(row=1, column=0, padx=14, pady=(0, 10), sticky="ew")

        # Ergebnis-Vorschau
        self._preview = ctk.CTkTextbox(
            right,
            font=ctk.CTkFont(family=FONT, size=FONT_BODY),
            wrap="word",
            fg_color=(LIGHT_CARD, DARK_CARD),
            border_width=1,
            border_color=("#c2cede", "#3a6a9a"),
            corner_radius=8,
            state="disabled",
        )
        self._preview.grid(row=2, column=0, padx=14, pady=(0, 10), sticky="nsew")

        # Starten-Button
        self._btn_start = ctk.CTkButton(
            right, text="▶  Alle Dateien verarbeiten",
            height=HEIGHT_BUTTON,
            font=ctk.CTkFont(family=FONT, size=FONT_BUTTON, weight="bold"),
            fg_color=BLUE_ACCENT, hover_color=NAVY_MED,
            corner_radius=8, command=self._start_batch,
        )
        self._btn_start.grid(row=3, column=0, padx=14, pady=(0, 8), sticky="ew")

        # Ergebnis übernehmen
        self._btn_accept = ctk.CTkButton(
            right, text="✓  Ergebnis ins Hauptfenster übernehmen",
            height=HEIGHT_BUTTON,
            font=ctk.CTkFont(family=FONT, size=FONT_BUTTON, weight="bold"),
            fg_color=SUCCESS, hover_color="#14803e",
            corner_radius=8, state="disabled", command=self._accept,
        )
        self._btn_accept.grid(row=4, column=0, padx=14, pady=(0, 12), sticky="ew")

    # ------------------------------------------------------------------ #
    #  Datei-Verwaltung                                                   #
    # ------------------------------------------------------------------ #

    def _add_files(self):
        exts_std = "*.pdf *.jpg *.jpeg *.png *.tiff *.tif *.bmp *.docx *.xlsx *.pptx"
        exts_pro = "*.txt *.odt *.rtf"
        paths = filedialog.askopenfilenames(
            title="Dateien für Batch auswählen",
            filetypes=[
                ("Alle unterstützten Dateien", f"{exts_std} {exts_pro}"),
                ("Standard-Formate", exts_std),
                ("PRO-Formate", exts_pro),
                ("Alle Dateien", "*.*"),
            ],
        )
        for p in paths:
            if p not in self._files:
                ext = os.path.splitext(p)[1].lower()
                if ext in ALL_SUPPORTED_EXTS:
                    self._files.append(p)
        self._refresh_list()

    def _on_drop(self, event):
        raw = event.data.strip()
        paths = self._parse_drop(raw)
        for p in paths:
            if os.path.isfile(p) and p not in self._files:
                ext = os.path.splitext(p)[1].lower()
                if ext in ALL_SUPPORTED_EXTS:
                    self._files.append(p)
        self._refresh_list()

    def _parse_drop(self, raw: str) -> list[str]:
        """Parst den Drop-Event-String (kann mehrere Pfade enthalten)."""
        import re
        # Tkinter DnD liefert Pfade in {} wenn Leerzeichen enthalten
        paths = re.findall(r'\{([^}]+)\}|(\S+)', raw)
        return [a or b for a, b in paths]

    def _remove_selected(self):
        for i in reversed(self._listbox.curselection()):
            self._files.pop(i)
        self._refresh_list()

    def _clear_list(self):
        self._files.clear()
        self._refresh_list()

    def _refresh_list(self):
        self._listbox.delete(0, "end")
        for p in self._files:
            self._listbox.insert("end", os.path.basename(p))
        n = len(self._files)
        self._lbl_count.configure(text=f"{n} Datei{'en' if n != 1 else ''} ausgewählt")

    # ------------------------------------------------------------------ #
    #  Batch-Verarbeitung                                                 #
    # ------------------------------------------------------------------ #

    def _start_batch(self):
        if not self._files:
            messagebox.showwarning("Keine Dateien", "Bitte zuerst Dateien hinzufügen.",
                                   parent=self)
            return
        self._btn_start.configure(state="disabled", text="⏳  Wird verarbeitet …")
        self._btn_accept.configure(state="disabled")
        self._progress.set(0)
        self._lbl_status.configure(text="Verarbeitung läuft …")

        total = len(self._files)

        def on_progress(current, tot, fname):
            self.after(0, lambda: self._update_progress(current, tot, fname))

        def on_done(results):
            self.after(0, lambda: self._finish_batch(results))

        process_batch(
            self._files,
            allow_pro=self._allow_pro,
            on_progress=on_progress,
            on_done=on_done,
        )

    def _update_progress(self, current: int, total: int, fname: str):
        self._progress.set(current / total)
        self._lbl_status.configure(
            text=f"Verarbeite {current}/{total}: {fname}"
        )

    def _finish_batch(self, results: dict[str, str]):
        self._results = results
        combined = combine_results(results)

        self._preview.configure(state="normal")
        self._preview.delete("0.0", "end")
        self._preview.insert("0.0", combined)
        self._preview.configure(state="disabled")

        n = len(results)
        self._lbl_status.configure(
            text=f"✓  {n} Datei{'en' if n != 1 else ''} verarbeitet."
        )
        self._progress.set(1.0)
        self._btn_start.configure(state="normal", text="▶  Alle Dateien verarbeiten")
        self._btn_accept.configure(state="normal")

    # ------------------------------------------------------------------ #
    #  Handler                                                            #
    # ------------------------------------------------------------------ #

    def _accept(self):
        self.result = combine_results(self._results)
        self.destroy()

    def _on_close(self):
        self.result = None
        self.destroy()
