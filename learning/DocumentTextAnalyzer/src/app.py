"""
app.py
DocumentTextAnalyzer - Design nach vt-solutions GmbH Website.
Navy-Blue Header, Segoe UI Schrift, cleanes professionelles Layout.
"""

import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image

from src.file_router import route_file
from src.ui.info_dialog import InfoDialog
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

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

SUPPORTED_EXTENSIONS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp",
    ".docx", ".xlsx", ".pptx"
}


class DocumentTextAnalyzerApp(TkinterDnD.Tk):
    """Hauptfenster im vt-solutions Corporate Design."""

    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        # Fenster zentriert starten (+30% groesser)
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w, h = 1430, 1010
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(1000, 720)
        self.configure(bg=DARK_BG)

        self._selected_file = ""
        self._is_dark = True

        self._set_window_icon()
        self._build_ui()
        self._setup_drag_and_drop()

    # ------------------------------------------------------------------ #
    #  Icon                                                               #
    # ------------------------------------------------------------------ #

    def _set_window_icon(self):
        icon_path = os.path.join(os.path.dirname(__file__), "..", ICON_PATH)
        if os.path.isfile(icon_path):
            try:
                self.iconbitmap(icon_path)
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
        self.header_frame = ctk.CTkFrame(
            self, fg_color=NAVY_DARK, corner_radius=0, height=86
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        # Spalte 0 = Logo (feste Breite), Spalte 1 = Titel (wächst), Spalte 2 = Buttons
        self.header_frame.grid_columnconfigure(0, minsize=200)
        self.header_frame.grid_columnconfigure(1, weight=1)
        self.header_frame.grid_columnconfigure(2, minsize=220)
        self.header_frame.grid_propagate(False)

        # ── Logo ──────────────────────────────────────────────────────
        logo_path = os.path.join(os.path.dirname(__file__), "..", LOGO_PATH)
        if os.path.isfile(logo_path):
            pil_orig = Image.open(logo_path).convert("RGBA")

            # Fuer dunklen Header: Pixel invertieren (schwarz -> weiss)
            r, g, b, a = pil_orig.split()
            pil_inv = Image.merge("RGBA", (
                r.point(lambda x: 255 - x),
                g.point(lambda x: 255 - x),
                b.point(lambda x: 255 - x),
                a,
            ))

            # Anzeigegroesse berechnen – Seitenverhaeltnis behalten
            # NICHT vorher skalieren: CTkImage nutzt das Originalbild -> scharfe Darstellung
            max_w, max_h = 200, 52
            orig_w, orig_h = pil_inv.size
            scale = min(max_w / orig_w, max_h / orig_h)
            dw = int(orig_w * scale)
            dh = int(orig_h * scale)

            # Originalbild (3400px breit) direkt an CTkImage uebergeben
            # size=(dw,dh) bestimmt nur die Darstellungsgroesse
            self._logo_img = ctk.CTkImage(
                light_image=pil_inv,
                dark_image=pil_inv,
                size=(dw, dh),
            )
            logo_widget = ctk.CTkLabel(
                self.header_frame, image=self._logo_img, text="", bg_color=NAVY_DARK
            )
        else:
            logo_widget = ctk.CTkLabel(
                self.header_frame,
                text=COMPANY_NAME,
                font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                text_color=WHITE,
                bg_color=NAVY_DARK,
            )
        logo_widget.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        # ── App-Titel ─────────────────────────────────────────────────
        # Titel + Untertitel in einer Spalte
        title_frame = ctk.CTkFrame(self.header_frame, fg_color=NAVY_DARK)
        title_frame.grid(row=0, column=1, sticky="w", padx=(0, 10), pady=12)

        ctk.CTkLabel(
            title_frame,
            text=APP_NAME,
            font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"),
            text_color=WHITE,
            bg_color=NAVY_DARK,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            title_frame,
            text="Texterkennung aus PDF-, Bild- und Office-Dateien",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color="#6b8caa",
            bg_color=NAVY_DARK,
            anchor="w",
        ).grid(row=1, column=0, sticky="w")

        # Buttons rechts
        btn_frame = ctk.CTkFrame(self.header_frame, fg_color=NAVY_DARK)
        btn_frame.grid(row=0, column=2, padx=(0, 20), pady=12, sticky="e")

        self.btn_theme = ctk.CTkButton(
            btn_frame,
            text="☀  Hell",
            width=105, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color="transparent",
            border_width=1,
            border_color="#4a6a8a",
            text_color=WHITE,
            hover_color=NAVY_MED,
            command=self._toggle_theme,
        )
        self.btn_theme.grid(row=0, column=0, padx=(0, 8))

        ctk.CTkButton(
            btn_frame,
            text="?  Hilfe",
            width=85, height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            fg_color="transparent",
            border_width=1,
            border_color="#4a6a8a",
            text_color=WHITE,
            hover_color=NAVY_MED,
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
        """Drag & Drop Zone – nur Dateiname-Anzeige, kein Button mehr."""
        self.drop_zone = ctk.CTkFrame(
            self.content_frame,
            fg_color=(LIGHT_CARD, DARK_CARD),
            corner_radius=10,
            border_width=2,
            border_color=("#c2cede", "#3a6a9a"),
            height=48,
        )
        self.drop_zone.grid(row=1, column=0, padx=24, pady=(0, 8), sticky="ew")
        self.drop_zone.grid_columnconfigure(0, weight=1)
        self.drop_zone.grid_propagate(False)

        self.lbl_file = ctk.CTkLabel(
            self.drop_zone,
            text="📂  Datei hier ablegen  oder  Schaltfläche nutzen",
            anchor="w",
            text_color=(TEXT_MUTED, "#6b8caa"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
        )
        self.lbl_file.grid(row=0, column=0, padx=16, sticky="ew")

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

    def _build_bottom_buttons(self):
        bar = ctk.CTkFrame(
            self.content_frame,
            fg_color=(LIGHT_BG, DARK_BG),
            corner_radius=0,
        )
        bar.grid(row=3, column=0, padx=24, pady=(0, 16), sticky="e")

        # 📋 Kopieren – Grün
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
        ).grid(row=0, column=0, padx=(0, 10))

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
        ).grid(row=0, column=1, padx=(0, 10))

        # 🗑 Leeren – Rot/Grau
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
        ).grid(row=0, column=2)

    # ---- FOOTER -------------------------------------------------------

    def _build_footer(self):
        footer = ctk.CTkFrame(
            self, fg_color=NAVY_DARK, corner_radius=0, height=38
        )
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)
        footer.grid_propagate(False)

        ctk.CTkLabel(
            footer,
            text=f"{COMPANY_NAME}  |  {COMPANY_EMAIL}  |  {COMPANY_WEBSITE}  |  Version {APP_VERSION}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color="#6b8caa",
            bg_color=NAVY_DARK,
        ).grid(row=0, column=0, pady=10)

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

    def _toggle_theme(self):
        if not self._is_dark:
            self._is_dark = True
            ctk.set_appearance_mode("Dark")
            self.configure(bg=DARK_BG)
            self.btn_theme.configure(text="☀  Hell")
        else:
            self._is_dark = False
            ctk.set_appearance_mode("Light")
            self.configure(bg=LIGHT_BG)
            self.btn_theme.configure(text="🌙  Dunkel")

    def _show_info(self):
        InfoDialog(self)

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
            text="Datei hier ablegen  oder  Schaltfläche nutzen",
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
