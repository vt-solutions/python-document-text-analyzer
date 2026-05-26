"""
app.py
DocumentTextAnalyzer - Design nach vt-solutions GmbH Website.
Navy-Blue Header, Segoe UI Schrift, cleanes professionelles Layout.
"""

import os
import threading
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image

from src.file_router import route_file
from src.ui.info_dialog import InfoDialog
from src.settings_manager import load as load_settings, save as save_settings
import src.licensing.license_manager as lm
from src.version import (
    APP_NAME, APP_VERSION,
    COMPANY_NAME, COMPANY_EMAIL, COMPANY_WEBSITE,
    LOGO_PATH, ICON_PATH,
)

# ------------------------------------------------------------------ #
#  Farbpalette - vt-solutions Website                                 #
# ------------------------------------------------------------------ #
NAVY_DARK    = "#0d1f35"   # Header-Hintergrund (wie Hero-Bereich)
NAVY_MED     = "#1a3a5c"   # Hover / sekundaere Elemente
BLUE_ACCENT  = "#1e5fd4"   # Buttons, Akzente
WHITE        = "#ffffff"
LIGHT_BG     = "#f4f6f9"   # Heller Seitenhintergrund
LIGHT_CARD   = "#ffffff"   # Kartenbereich (Textbox, Drop-Zone)
DARK_BG      = "#0d1520"   # Dunkelmodus Hintergrund
DARK_CARD    = "#132030"   # Dunkelmodus Karten
TEXT_MUTED   = "#6b7c93"   # Grauer Hinweistext

FONT_FAMILY  = "Segoe UI"  # Naechste Alternative zur Website-Schrift

# Theme-Bezeichnungen für den Segmented-Button
THEME_LIGHT = "☀  Hellmodus"
THEME_DARK  = "🌙  Dunkelmodus"

# Gespeichertes Theme laden (Fallback: Dark)
_saved = load_settings()
ctk.set_appearance_mode(_saved.get("theme", "Dark"))
ctk.set_default_color_theme("blue")

SUPPORTED_EXTENSIONS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp",
    ".docx", ".xlsx", ".pptx"
}


class DocumentTextAnalyzerApp(TkinterDnD.Tk):
    """Hauptfenster im vt-solutions Corporate Design."""

    def __init__(self):
        super().__init__()

        # ── Lizenz prüfen BEVOR das Fenster je sichtbar wird ─────────
        _needs_license = lm.is_first_run() or lm.is_trial_expired()
        if _needs_license:
            self.withdraw()   # sofort verstecken – kein Flackern

        self.title(APP_NAME)
        self.minsize(920, 680)

        # Startgröße zentriert auf dem Bildschirm
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w  = min(1800, sw - 40)
        h  = min(1050, sh - 80)
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._selected_file = ""
        self._is_dark = (_saved.get("theme", "Dark") == "Dark")
        self.configure(bg=DARK_BG if self._is_dark else LIGHT_BG)

        self._set_window_icon()
        self._build_ui()
        self._setup_drag_and_drop()

        if _needs_license:
            self.after(60, self._check_license_on_startup)

    # ------------------------------------------------------------------ #
    #  Icon                                                               #
    # ------------------------------------------------------------------ #

    def _set_window_icon(self):
        """
        Setzt das VT-Icon für Titelleiste, Taskleiste und ALT+TAB.

        Zwei Methoden kombiniert:
          1. iconbitmap()   – Tkinter, Titelleiste
          2. WM_SETICON     – Windows-API, Taskleiste + ALT+TAB

        Pfad:
          EXE  → sys._MEIPASS/assets/app.ico
          Skript → <projektroot>/assets/app.ico
        """
        import sys
        base = (sys._MEIPASS
                if hasattr(sys, "_MEIPASS")
                else os.path.normpath(
                    os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
                ))
        ico_path = os.path.abspath(os.path.join(base, ICON_PATH))

        if not os.path.isfile(ico_path):
            return  # ICO-Datei nicht gefunden → Standard-Icon bleibt

        # ── Methode 1: Tkinter (Titelleiste) ─────────────────────────
        try:
            self.iconbitmap(ico_path)
        except Exception:
            pass

        # ── Methode 2: Windows-API (Taskleiste + ALT+TAB) ────────────
        # after() stellt sicher, dass der HWND bereits existiert
        self.after(150, lambda p=ico_path: self._apply_taskbar_icon(p))

    def _apply_taskbar_icon(self, ico_path: str):
        """
        Setzt das Icon direkt über WM_SETICON auf den Windows-HWND.
        Funktioniert auch wenn die App als python.exe-Prozess läuft.
        """
        try:
            import ctypes
            user32 = ctypes.windll.user32

            IMAGE_ICON      = 1
            LR_LOADFROMFILE = 0x0010
            LR_DEFAULTSIZE  = 0x0040
            WM_SETICON      = 0x0080
            ICON_SMALL      = 0
            ICON_BIG        = 1
            GA_ROOT         = 2   # GetAncestor: Root-Fenster holen

            # Großes (256 px) und kleines (16 px) Icon laden
            h_big   = user32.LoadImageW(
                None, ico_path, IMAGE_ICON, 0, 0,
                LR_LOADFROMFILE | LR_DEFAULTSIZE
            )
            h_small = user32.LoadImageW(
                None, ico_path, IMAGE_ICON, 16, 16,
                LR_LOADFROMFILE
            )

            # HWND des echten Top-Level-Fensters ermitteln
            hwnd = user32.GetAncestor(self.winfo_id(), GA_ROOT)
            if not hwnd:
                hwnd = user32.GetParent(self.winfo_id()) or self.winfo_id()

            if hwnd:
                if h_big:   user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG,   h_big)
                if h_small: user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, h_small)
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  UI aufbauen                                                        #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Header – feste Höhe
        self.grid_rowconfigure(1, weight=1)  # Content – wächst mit Fenster
        self.grid_rowconfigure(2, weight=0)  # Footer – feste Höhe

        self._build_header()
        self._build_content()
        self._build_footer()

    # ---- HEADER (immer Navy-Dunkel wie die Website) -------------------

    def _build_header(self):
        # Header-Hintergrund: Navy im Dark Mode, Weiß im Light Mode
        self.header_frame = ctk.CTkFrame(
            self, fg_color=(LIGHT_CARD, NAVY_DARK), corner_radius=0, height=86
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        # Spalte 0 = Logo (feste Mindestbreite)
        # Spalte 1 = Titel (wächst, nimmt ganzen übrigen Platz)
        # Spalte 2 = Buttons (auto-Breite nach Inhalt – kein festes minsize,
        #            damit breiterer SegmentedButton nicht in Titel-Spalte einbricht)
        self.header_frame.grid_columnconfigure(0, weight=0, minsize=220)
        self.header_frame.grid_columnconfigure(1, weight=1, minsize=200)
        self.header_frame.grid_columnconfigure(2, weight=0)
        self.header_frame.grid_propagate(False)

        # ── Logo ──────────────────────────────────────────────────────
        import sys
        _base     = (sys._MEIPASS
                     if hasattr(sys, "_MEIPASS")
                     else os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
        logo_path = os.path.join(_base, LOGO_PATH)
        if os.path.isfile(logo_path):
            pil_orig = Image.open(logo_path).convert("RGBA")

            # Invertierte Version (weiß) für dunklen Header
            r, g, b, a = pil_orig.split()
            pil_inv = Image.merge("RGBA", (
                r.point(lambda x: 255 - x),
                g.point(lambda x: 255 - x),
                b.point(lambda x: 255 - x),
                a,
            ))

            # Anzeigegroesse – Seitenverhaeltnis behalten, Originalbild ungescalt übergeben
            max_w, max_h = 200, 52
            orig_w, orig_h = pil_orig.size
            scale = min(max_w / orig_w, max_h / orig_h)
            dw = int(orig_w * scale)
            dh = int(orig_h * scale)

            # light_image = original (dunkel, für hellen Header)
            # dark_image  = invertiert (weiß, für dunklen Header)
            self._logo_img = ctk.CTkImage(
                light_image=pil_orig,
                dark_image=pil_inv,
                size=(dw, dh),
            )
            logo_widget = ctk.CTkLabel(
                self.header_frame, image=self._logo_img, text="",
                bg_color=(LIGHT_CARD, NAVY_DARK),
            )
        else:
            logo_widget = ctk.CTkLabel(
                self.header_frame,
                text=COMPANY_NAME,
                font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                text_color=(NAVY_DARK, WHITE),
                bg_color=(LIGHT_CARD, NAVY_DARK),
            )
        logo_widget.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        # ── App-Titel ─────────────────────────────────────────────────
        # sticky="ew" + grid_columnconfigure weight=1 → Frame füllt Spalte 1 vollständig
        title_frame = ctk.CTkFrame(self.header_frame, fg_color=(LIGHT_CARD, NAVY_DARK))
        title_frame.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=12)
        title_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_frame,
            text=APP_NAME,
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=(NAVY_DARK, WHITE),
            bg_color=(LIGHT_CARD, NAVY_DARK),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 4))

        ctk.CTkLabel(
            title_frame,
            text="Texterkennung aus PDF-, Bild- und Office-Dateien",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=(TEXT_MUTED, "#6b8caa"),
            bg_color=(LIGHT_CARD, NAVY_DARK),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=(0, 4))

        # ── Buttons rechts ────────────────────────────────────────────
        btn_frame = ctk.CTkFrame(self.header_frame, fg_color=(LIGHT_CARD, NAVY_DARK))
        btn_frame.grid(row=0, column=2, padx=(0, 20), pady=12, sticky="e")

        # ── Theme-Umschalter als Segmented Button ────────────────────
        self.seg_theme = ctk.CTkSegmentedButton(
            btn_frame,
            values=[THEME_LIGHT, THEME_DARK],
            command=self._on_theme_change,
            height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            # Text immer Weiß – funktioniert auf allen Hintergründen
            text_color=WHITE,
            text_color_disabled="#7a9ab8",
            # Aktiver State: kräftige Farbe, klar erkennbar
            selected_color=(NAVY_DARK, BLUE_ACCENT),     # Hell: Navy | Dunkel: Blau
            selected_hover_color=(NAVY_MED, "#1a4fa8"),
            # Inaktiver State: mittleres Blau-Grau, Weißtext hat ~6:1 Kontrast
            unselected_color=("#4a6a8a", "#1a3550"),     # Hell: mittelblau | Dunkel: dunkelnavy
            unselected_hover_color=("#3a5a7a", NAVY_MED),
            # Container-Hintergrund
            fg_color=("#3a5a7a", NAVY_MED),
            corner_radius=8,
        )
        self.seg_theme.set(THEME_DARK if self._is_dark else THEME_LIGHT)
        self.seg_theme.grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="?  Hilfe",
            width=85, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color="transparent",
            border_width=1,
            border_color=("#c2cede", "#4a6a8a"),
            text_color=(NAVY_DARK, WHITE),
            hover_color=(LIGHT_BG, NAVY_MED),
            command=self._show_info,
        ).grid(row=0, column=1)

    # ---- CONTENT BEREICH ----------------------------------------------

    def _build_content(self):
        self.content_frame = ctk.CTkFrame(
            self,
            fg_color=(LIGHT_BG, DARK_BG),
            corner_radius=0,
        )
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Action-Bar (Buttons)
        self.content_frame.grid_rowconfigure(1, weight=0)  # Drop-Zone (Dateiname)
        self.content_frame.grid_rowconfigure(2, weight=1)  # Textbox – wächst
        self.content_frame.grid_rowconfigure(3, weight=0)  # Bottom-Buttons

        self._build_action_bar()
        self._build_drop_zone()
        self._build_textbox()
        self._build_bottom_buttons()

    def _build_action_bar(self):
        """Aktionsleiste: beide Buttons nebeneinander, außerhalb des Rahmens."""
        bar = ctk.CTkFrame(
            self.content_frame,
            fg_color=(LIGHT_BG, DARK_BG),
            corner_radius=0,
        )
        bar.grid(row=0, column=0, padx=24, pady=(20, 8), sticky="ew")
        bar.grid_columnconfigure(2, weight=1)  # Status bekommt den Rest

        # ── Datei auswählen ──────────────────────────────────────────
        self.btn_choose = ctk.CTkButton(
            bar,
            text="📂  Datei auswählen",
            width=185, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=BLUE_ACCENT,
            hover_color=NAVY_MED,
            corner_radius=8,
            command=self._choose_file,
        )
        self.btn_choose.grid(row=0, column=0, padx=(0, 10))

        # ── Text erkennen ────────────────────────────────────────────
        self.btn_extract = ctk.CTkButton(
            bar,
            text="🔍  Text erkennen",
            width=175, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color=NAVY_DARK,
            hover_color=NAVY_MED,
            corner_radius=8,
            state="disabled",
            command=self._start_extraction,
        )
        # btn_extract wird NICHT gegriddet – Auto-Extraktion übernimmt die Funktion.
        # Widget bleibt als Objekt erhalten (state-Verwaltung in _start_extraction/_show_result).

        # Fortschrittsbalken (eingeblendet während der Verarbeitung)
        self.progress = ctk.CTkProgressBar(
            bar, width=175, mode="indeterminate",
            fg_color=("#dce3ec", "#1e3a5a"),
            progress_color=BLUE_ACCENT,
        )
        self.progress.grid(row=0, column=1, padx=(0, 14))
        self.progress.grid_remove()

        # Statusmeldung
        self.lbl_status = ctk.CTkLabel(
            bar, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=(TEXT_MUTED, "#6b8caa"),
        )
        self.lbl_status.grid(row=0, column=2, sticky="w")

    def _build_drop_zone(self):
        """Drag & Drop Zone – Rahmen auf allen 4 Seiten vollständig sichtbar.

        Ursache fehlender oberer Border:
          grid_propagate(False) + height=48 zwang den CTkFrame-Canvas in eine
          zu enge Box – der obere Rand wurde außerhalb gezeichnet.
        Fix: keine feste Höhe, kein grid_propagate(False).
          Das Label-pady innen bestimmt die Gesamthöhe des Feldes.
        """
        self.drop_zone = ctk.CTkFrame(
            self.content_frame,
            fg_color=(LIGHT_CARD, DARK_CARD),
            corner_radius=10,
            border_width=2,
            border_color=("#c2cede", "#3a6a9a"),
            # KEIN height= und KEIN grid_propagate(False) –
            # Frame passt sich dem Inhalt an → alle 4 Border sichtbar
        )
        self.drop_zone.grid(row=1, column=0, padx=24, pady=(4, 8), sticky="ew")
        self.drop_zone.grid_columnconfigure(0, weight=1)

        self.lbl_file = ctk.CTkLabel(
            self.drop_zone,
            text="📂  Datei hier ablegen  –  oder Schaltfläche nutzen",
            anchor="w",
            text_color=(TEXT_MUTED, "#6b8caa"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        )
        # pady=13 → kontrolliert die Höhe des Feldes (entspricht ~48 px gesamt)
        self.lbl_file.grid(row=0, column=0, padx=16, pady=13, sticky="ew")

    def _build_textbox(self):
        self.textbox = ctk.CTkTextbox(
            self.content_frame,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            wrap="word",
            fg_color=(LIGHT_CARD, DARK_CARD),
            border_width=2,
            border_color=("#c2cede", "#3a6a9a"),
            corner_radius=10,
            scrollbar_button_color=(BLUE_ACCENT, BLUE_ACCENT),
        )
        self.textbox.grid(row=2, column=0, padx=24, pady=(0, 8), sticky="nsew")
        self.textbox.insert("0.0", "Hier erscheint der erkannte Text …")
        self.textbox.configure(state="disabled")

        # Rechtsklick-Menü + Tastenkürzel einrichten
        self._setup_textbox_extras()

    def _setup_textbox_extras(self):
        """Rechtsklick-Kontextmenü und Tastenkürzel für den Texteditor."""
        dark = self._is_dark

        # ── Kontextmenü (systemnahes tk.Menu mit Corporate-Farben) ───
        self._ctx_menu = tk.Menu(
            self, tearoff=0,
            font=(FONT_FAMILY, 11),
            bg="#132030"    if dark else "#ffffff",
            fg="#e8eaf0"    if dark else NAVY_DARK,
            activebackground=BLUE_ACCENT,
            activeforeground="#ffffff",
            relief="flat", bd=1,
        )
        self._ctx_menu.add_command(
            label="📋  Kopieren",
            command=self._copy_selected_text,
            accelerator="Strg+C",
        )
        self._ctx_menu.add_command(
            label="☑  Alles markieren",
            command=self._select_all_text,
            accelerator="Strg+A",
        )
        self._ctx_menu.add_separator()
        self._ctx_menu.add_command(
            label="📄  Alles kopieren",
            command=self._copy_text,
        )

        # Binding auf CTkTextbox-Wrapper UND internen tk.Text Widget
        _inner = getattr(self.textbox, "_textbox", None)
        for w in filter(None, [self.textbox, _inner]):
            w.bind("<Button-3>", self._show_ctx_menu)
            w.bind("<Control-a>", lambda e: (self._select_all_text(), "break")[1])
            w.bind("<Control-A>", lambda e: (self._select_all_text(), "break")[1])

    def _show_ctx_menu(self, event):
        """Zeigt das Rechtsklick-Menü an der Mausposition."""
        try:
            sel = self.textbox.get("sel.first", "sel.last")
            has_sel = bool(sel.strip())
        except Exception:
            has_sel = False

        # "Kopieren" nur aktiv wenn etwas markiert ist
        self._ctx_menu.entryconfig(0, state="normal" if has_sel else "disabled")

        try:
            self._ctx_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._ctx_menu.grab_release()
        return "break"

    def _select_all_text(self):
        """Markiert den gesamten Text im Textfeld (Strg+A)."""
        _inner = getattr(self.textbox, "_textbox", self.textbox)
        self.textbox.configure(state="normal")
        _inner.tag_add("sel", "1.0", "end-1c")
        self.textbox.configure(state="disabled")
        self.textbox.focus_set()

    def _copy_selected_text(self):
        """Kopiert nur den aktuell markierten Text."""
        try:
            text = self.textbox.get("sel.first", "sel.last")
            if text.strip():
                self.clipboard_clear()
                self.clipboard_append(text)
                self._set_status(f"Markierung kopiert  ({len(text)} Zeichen) ✓")
            else:
                messagebox.showinfo(
                    "Kein Text markiert",
                    "Bitte zuerst Text im Editor markieren\n"
                    "(Maus ziehen oder Strg+A für alles).",
                )
        except Exception:
            messagebox.showinfo(
                "Kein Text markiert",
                "Bitte zuerst Text im Editor markieren\n"
                "(Maus ziehen oder Strg+A für alles).",
            )

    def _build_bottom_buttons(self):
        bar = ctk.CTkFrame(
            self.content_frame,
            fg_color=(LIGHT_BG, DARK_BG),
            corner_radius=0,
        )
        bar.grid(row=3, column=0, padx=24, pady=(0, 16), sticky="e")

        # ✂ Markierten Text kopieren – Blau (NEU)
        ctk.CTkButton(
            bar,
            text="✂  Markierten Text kopieren",
            width=220, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=BLUE_ACCENT,
            hover_color=NAVY_MED,
            text_color=WHITE,
            corner_radius=8,
            command=self._copy_selected_text,
        ).grid(row=0, column=0, padx=(0, 10))

        # 📋 Alles kopieren – Grün
        ctk.CTkButton(
            bar,
            text="📋  Alles kopieren",
            width=170, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color="#1a7a4a",
            hover_color="#145f39",
            text_color=WHITE,
            corner_radius=8,
            command=self._copy_text,
        ).grid(row=0, column=1, padx=(0, 10))

        # 💾 Speichern – Navy
        ctk.CTkButton(
            bar,
            text="💾  Text speichern",
            width=170, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color=NAVY_DARK,
            hover_color=NAVY_MED,
            corner_radius=8,
            command=self._save_text,
        ).grid(row=0, column=2, padx=(0, 10))

        # 🗑 Leeren – Rot
        ctk.CTkButton(
            bar,
            text="🗑  Text leeren",
            width=150, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            fg_color="#b91c1c",
            hover_color="#991818",
            text_color=WHITE,
            corner_radius=8,
            command=self._clear_text,
        ).grid(row=0, column=3)

    # ---- FOOTER -------------------------------------------------------

    def _build_footer(self):
        footer = ctk.CTkFrame(
            self, fg_color=NAVY_DARK, corner_radius=0, height=38
        )
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=0)   # Lizenz-Status
        footer.grid_columnconfigure(1, weight=1)   # Abstand
        footer.grid_columnconfigure(2, weight=0)   # Firmendaten
        footer.grid_columnconfigure(3, weight=0)   # Lizenz-Button
        footer.grid_propagate(False)

        # ── Lizenzstatus (links) ──────────────────────────────────────
        status_text  = lm.get_status_text()
        status_color = "#16a34a" if lm.is_activated() else (
                       "#e87a2a" if not lm.is_trial_expired() else "#dc2626"
        )
        self.lbl_license = ctk.CTkLabel(
            footer,
            text=f"🔑  {status_text}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=status_color,
            bg_color=NAVY_DARK,
        )
        self.lbl_license.grid(row=0, column=0, padx=(16, 0), pady=10, sticky="w")

        # ── Firmendaten (mitte-rechts) ────────────────────────────────
        ctk.CTkLabel(
            footer,
            text=f"{COMPANY_NAME}  |  {COMPANY_EMAIL}  |  {COMPANY_WEBSITE}  |  Version {APP_VERSION}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color="#6b8caa",
            bg_color=NAVY_DARK,
        ).grid(row=0, column=2, pady=10)

        # ── Lizenz-Button (rechts) ────────────────────────────────────
        ctk.CTkButton(
            footer,
            text="Lizenz",
            width=70, height=22,
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            fg_color="transparent",
            border_width=1,
            border_color="#2a4a6a",
            text_color="#6b8caa",
            hover_color=NAVY_MED,
            corner_radius=4,
            command=self._show_license_dialog,
        ).grid(row=0, column=3, padx=(8, 16), pady=10)

    # ------------------------------------------------------------------ #
    #  Drag & Drop                                                        #
    # ------------------------------------------------------------------ #

    def _setup_drag_and_drop(self):
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self._on_drop)
        self.drop_zone.drop_target_register(DND_FILES)
        self.drop_zone.dnd_bind("<<Drop>>", self._on_drop)
        self.drop_zone.dnd_bind("<<DragEnter>>", self._on_drag_enter)
        self.drop_zone.dnd_bind("<<DragLeave>>", self._on_drag_leave)

    def _on_drag_enter(self, event):
        self.drop_zone.configure(border_color=BLUE_ACCENT, border_width=2)

    def _on_drag_leave(self, event):
        self.drop_zone.configure(border_color=("#dce3ec", "#1e3a5a"), border_width=2)

    def _on_drop(self, event):
        self.drop_zone.configure(border_color=("#dce3ec", "#1e3a5a"))
        raw = event.data.strip()
        if raw.startswith("{") and raw.endswith("}"):
            raw = raw[1:-1]
        path = raw.strip('"')
        if not os.path.isfile(path):
            self._set_status("⚠  Ungültige Datei")
            return
        ext = os.path.splitext(path)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            messagebox.showwarning(
                "Nicht unterstützt",
                f"Dateityp '{ext}' wird nicht unterstützt.\n\n"
                "Unterstützt: PDF, JPG, PNG, TIFF, DOCX, XLSX, PPTX"
            )
            return
        self._load_file(path)

    # ------------------------------------------------------------------ #
    #  Theme                                                              #
    # ------------------------------------------------------------------ #

    def _on_theme_change(self, value: str):
        """Wird vom CTkSegmentedButton aufgerufen wenn Hellmodus/Dunkelmodus gewählt."""
        if value == THEME_LIGHT:
            self._is_dark = False
            ctk.set_appearance_mode("Light")
            self.configure(bg=LIGHT_BG)
            save_settings({"theme": "Light"})
        else:
            self._is_dark = True
            ctk.set_appearance_mode("Dark")
            self.configure(bg=DARK_BG)
            save_settings({"theme": "Dark"})

    def _show_info(self):
        InfoDialog(self)

    def _check_license_on_startup(self):
        """
        Erster-Start / Trial-abgelaufen: Lizenzdialog anzeigen.
        App ist bereits erstellt (withdraw), Hauptfenster wird danach
        eingeblendet (deiconify) oder beendet (destroy).
        """
        from src.ui.license_dialog import LicenseDialog
        dlg = LicenseDialog(self)
        self.wait_window(dlg)

        if dlg.result is None:
            # Benutzer hat Dialog mit X geschlossen → App beenden
            self.destroy()
            return

        # Lizenz aktiviert oder Trial gestartet → Hauptfenster zeigen
        self._refresh_license_status()
        self.deiconify()
        self.lift()
        self.focus_force()

    def _show_license_dialog(self):
        """Lizenz-Dialog öffnen (Aktivierung / Infos)."""
        from src.ui.license_dialog import LicenseDialog
        dlg = LicenseDialog(self)
        self.wait_window(dlg)
        # Footer-Status nach Dialog aktualisieren
        self._refresh_license_status()

    def _refresh_license_status(self):
        """Aktualisiert den Lizenzstatus-Text im Footer."""
        status_text  = lm.get_status_text()
        status_color = "#16a34a" if lm.is_activated() else (
                       "#e87a2a" if not lm.is_trial_expired() else "#dc2626"
        )
        self.lbl_license.configure(
            text=f"🔑  {status_text}",
            text_color=status_color,
        )

    # ------------------------------------------------------------------ #
    #  Datei laden & Extraktion                                           #
    # ------------------------------------------------------------------ #

    def _choose_file(self):
        filetypes = [
            ("Alle unterstützten Dateien",
             "*.pdf *.jpg *.jpeg *.png *.tiff *.tif *.bmp *.docx *.xlsx *.pptx"),
            ("PDF-Dateien", "*.pdf"),
            ("Bilder", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp"),
            ("Word-Dokumente", "*.docx"),
            ("Excel-Tabellen", "*.xlsx"),
            ("PowerPoint", "*.pptx"),
            ("Alle Dateien", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Datei auswählen", filetypes=filetypes)
        if path:
            self._load_file(path)

    def _load_file(self, path: str):
        self._selected_file = path
        filename = os.path.basename(path)
        self.lbl_file.configure(
            text=f"📄  {filename}",
            text_color=(NAVY_DARK, WHITE),
        )
        self.btn_extract.configure(state="normal")
        self._set_status("")
        # Texterkennung automatisch starten
        self.after(100, self._start_extraction)

    def _start_extraction(self):
        if not self._selected_file:
            return
        self.btn_extract.configure(state="disabled")
        self.btn_choose.configure(state="disabled")
        self.progress.grid()
        self.progress.start()
        self._set_status("Verarbeite …")
        threading.Thread(target=self._run_extraction, daemon=True).start()

    def _run_extraction(self):
        try:
            result = route_file(self._selected_file)
        except Exception as e:
            result = f"Unerwarteter Fehler: {e}"
        self.after(0, self._show_result, result)

    def _show_result(self, text: str):
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", text)
        self.textbox.configure(state="disabled")
        self.progress.stop()
        self.progress.grid_remove()
        self.btn_extract.configure(state="normal")
        self.btn_choose.configure(state="normal")
        self._set_status("Fertig ✓")

    # ------------------------------------------------------------------ #
    #  Kopieren, Speichern & Leeren                                       #
    # ------------------------------------------------------------------ #

    def _clear_text(self):
        """Textfeld leeren, Dateiauswahl und Status zurücksetzen."""
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", "Hier erscheint der erkannte Text …")
        self.textbox.configure(state="disabled")

        self._selected_file = ""
        self.lbl_file.configure(
            text="📂  Datei hier ablegen  –  oder Schaltfläche nutzen",
            text_color=(TEXT_MUTED, "#6b8caa"),
        )
        self.btn_extract.configure(state="disabled")
        self._set_status("")

    def _copy_text(self):
        text = self.textbox.get("0.0", "end").strip()
        if not text:
            messagebox.showinfo("Info", "Kein Text zum Kopieren vorhanden.")
            return
        self.clipboard_clear()
        self.clipboard_append(text)
        self._set_status("Text kopiert ✓")

    def _save_text(self):
        text = self.textbox.get("0.0", "end").strip()
        if not text:
            messagebox.showinfo("Info", "Kein Text zum Speichern vorhanden.")
            return
        default_name = "erkannter_text.txt"
        if self._selected_file:
            base = os.path.splitext(os.path.basename(self._selected_file))[0]
            default_name = f"{base}_text.txt"
        save_path = filedialog.asksaveasfilename(
            title="Text speichern", defaultextension=".txt",
            initialfile=default_name,
            filetypes=[("Textdatei", "*.txt"), ("Alle Dateien", "*.*")],
        )
        if save_path:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            self._set_status(f"Gespeichert: {os.path.basename(save_path)} ✓")

    def _set_status(self, message: str):
        self.lbl_status.configure(text=message)
