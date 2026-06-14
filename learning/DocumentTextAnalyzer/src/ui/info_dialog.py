"""
info_dialog.py
Hilfe- und Info-Dialog fuer VT Document Text Converter.
Zeigt Funktionsbeschreibung, Formate, OCR-Hinweise und Firmendaten.
"""

import os
import tkinter as tk
import customtkinter as ctk
from PIL import Image

from src.version import (
    APP_NAME, APP_VERSION,
    COMPANY_NAME, COMPANY_EMAIL, COMPANY_WEBSITE,
    COPYRIGHT, LOGO_PATH, ICON_PATH,
)

FONT      = "Segoe UI"
NAVY      = "#0d1f35"
BLUE      = "#1e5fd4"
LIGHT_BG  = "#f4f6f9"
DARK_BG   = "#1a1a2e"
CARD_L    = "#ffffff"
CARD_D    = "#132030"
SEP_L     = "#dce3ec"
SEP_D     = "#1e3a5a"


class InfoDialog(tk.Toplevel):
    """
    Hilfe-Dialog mit Beschreibung, Formaten und Firmendaten.
    Basiert auf tk.Toplevel (kompatibel mit TkinterDnD.Tk).
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.title(f"Hilfe  –  {APP_NAME}")
        self.resizable(True, True)

        self._is_dark = ctk.get_appearance_mode() == "Dark"
        bg = DARK_BG if self._is_dark else LIGHT_BG
        self.configure(bg=bg)

        # VT-Icon setzen (Titelleiste + ALT+TAB)
        import sys
        _base    = (sys._MEIPASS
                    if hasattr(sys, "_MEIPASS")
                    else os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..")))
        ico_path = os.path.join(_base, ICON_PATH)
        if os.path.isfile(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

        dw, dh = 900, 900
        self._center(parent, dw, dh)
        self.minsize(700, 640)

        self._build_ui()
        self.after(60, self._make_modal)

    def _make_modal(self):
        try:
            self.grab_set()
            self.focus_force()
        except Exception:
            pass

    def _center(self, parent, dw, dh):
        parent.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width()  - dw) // 2
        y = parent.winfo_y() + (parent.winfo_height() - dh) // 2
        self.geometry(f"{dw}x{dh}+{x}+{y}")

    # ------------------------------------------------------------------ #
    #  UI                                                                  #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        dark  = self._is_dark
        bg    = DARK_BG  if dark else LIGHT_BG
        card  = CARD_D   if dark else CARD_L
        sep   = SEP_D    if dark else SEP_L
        txt   = "#e8eaf0" if dark else NAVY
        muted = "#6b8caa" if dark else "#6b7c93"

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header – Logo + Untertitel zentriert mit pack ────────────
        hdr = tk.Frame(self, bg=NAVY)
        hdr.grid(row=0, column=0, sticky="ew")

        logo_path = os.path.join(os.path.dirname(__file__), "..", "..", LOGO_PATH)
        if os.path.isfile(logo_path):
            pil = Image.open(logo_path).convert("RGBA")
            r, g, b, a = pil.split()
            pil_inv = Image.merge("RGBA", (
                r.point(lambda x: 255 - x),
                g.point(lambda x: 255 - x),
                b.point(lambda x: 255 - x), a,
            ))
            max_w, max_h = 220, 60
            ow, oh = pil_inv.size
            sc = min(max_w / ow, max_h / oh)
            dw2, dh2 = int(ow * sc), int(oh * sc)
            self._logo = ctk.CTkImage(light_image=pil_inv, dark_image=pil_inv, size=(dw2, dh2))
            logo_lbl = ctk.CTkLabel(hdr, image=self._logo, text="", bg_color=NAVY)
            logo_lbl.pack(pady=(18, 4))
        else:
            tk.Label(hdr, text=COMPANY_NAME,
                     font=(FONT, 14, "bold"), fg="#ffffff", bg=NAVY).pack(pady=(18, 4))

        tk.Label(hdr, text="Hilfe & Informationen",
                 font=(FONT, 10), fg="#6b8caa", bg=NAVY).pack(pady=(0, 14))

        # ── Scrollbarer Bereich ───────────────────────────────────────
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=(LIGHT_BG, DARK_BG),
            scrollbar_button_color=BLUE,
        )
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        scroll_frame.grid_columnconfigure(0, weight=1)

        sf = scroll_frame   # Kurzname

        # ── Hilfs-Funktionen ──────────────────────────────────────────

        def make_card(title_text):
            """Erstellt eine Karte und gibt den Frame zurück."""
            frame = ctk.CTkFrame(
                sf,
                fg_color=(CARD_L, CARD_D),
                corner_radius=10,
                border_width=1,
                border_color=(SEP_L, SEP_D),
            )
            frame.grid(sticky="ew", padx=20, pady=(0, 10))
            frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                frame, text=title_text,
                font=ctk.CTkFont(family=FONT, size=13, weight="bold"),
                text_color=(NAVY, "#e8eaf0"),
                anchor="w",
            ).grid(sticky="w", padx=14, pady=(10, 4))

            ctk.CTkFrame(frame, height=1, fg_color=(SEP_L, SEP_D)).grid(
                sticky="ew", padx=14, pady=(0, 6)
            )
            return frame

        def add_row(frame, text, top=2, bottom=2):
            """Fügt eine Textzeile zur Karte hinzu."""
            ctk.CTkLabel(
                frame, text=text,
                font=ctk.CTkFont(family=FONT, size=12),
                text_color=("#334155", "#c0cfe0"),
                anchor="w", justify="left",
            ).grid(sticky="w", padx=20, pady=(top, bottom))

        def add_gap(frame, h=5):
            """Kleiner Abstandshalter innerhalb einer Karte."""
            ctk.CTkFrame(frame, height=h, fg_color="transparent").grid()

        def add_subtitle(frame, text):
            """Grauer Untertitel / Kategoriename innerhalb einer Karte."""
            ctk.CTkLabel(
                frame, text=text,
                font=ctk.CTkFont(family=FONT, size=11, weight="bold"),
                text_color=("#6b7c93", "#6b8caa"),
                anchor="w",
            ).grid(sticky="w", padx=20, pady=(6, 1))

        # Abstand oben
        ctk.CTkFrame(sf, height=12, fg_color="transparent").grid()

        # ── 1. Was macht diese App? ───────────────────────────────────
        c1 = make_card("📄  Was macht diese App?")
        add_row(c1, "VT Document Text Converter extrahiert automatisch Text")
        add_row(c1, "aus Dokumenten und macht ihn kopierbar oder speicherbar.")
        add_gap(c1, 4)
        add_row(c1, "Ideal für: Rechnungen · Scans · Verträge · Screenshots")
        add_gap(c1, 8)

        # ── 2. Unterstützte Formate ───────────────────────────────────
        c2 = make_card("📁  Unterstützte Dateiformate")
        add_subtitle(c2, "Standard  (alle Editionen)")
        add_row(c2, "  PDF-Dateien (mit Text)   →  direkte Textextraktion")
        add_row(c2, "  Gescannte PDF             →  OCR-Erkennung")
        add_row(c2, "  JPG · PNG · TIFF · BMP   →  OCR-Bilderkennung")
        add_row(c2, "  Word  (.docx)             →  Text direkt lesen")
        add_row(c2, "  Excel  (.xlsx)            →  Zellinhalte lesen")
        add_row(c2, "  PowerPoint  (.pptx)       →  Folientexte lesen")
        add_subtitle(c2, "PRO-Edition")
        add_row(c2, "  Textdateien  (.txt)       →  direkte Extraktion")
        add_row(c2, "  LibreOffice Writer (.odt) →  direkte Extraktion")
        add_row(c2, "  Rich Text Format  (.rtf)  →  direkte Extraktion")
        add_gap(c2, 8)

        # ── 3. Funktionen ─────────────────────────────────────────────
        c3 = make_card("⚙️  Funktionen")
        add_subtitle(c3, "Standard & Trial")
        for line in [
            "  ✓  Datei auswählen oder per Drag & Drop ablegen",
            "  ✓  Automatische Erkennung beim Öffnen der Datei",
            "  ✓  PDF-Text direkt extrahieren",
            "  ✓  Bilder und Scans per OCR erkennen  (DE + EN)",
            "  ✓  Office-Dokumente vollständig auslesen",
            "  ✓  Erkannten Text kopieren (Auswahl oder alles)",
            "  ✓  Text als .txt-Datei speichern",
        ]:
            add_row(c3, line, top=2, bottom=2)
        add_subtitle(c3, "PRO-Edition  (zusätzlich)")
        for line in [
            "  ✓  Erweiterte Eingabeformate  (.txt · .odt · .rtf)",
            "  ✓  Export als DOCX  (Word-Dokument)",
            "  ✓  Export als PDF",
            "  ✓  Batch-Verarbeitung mehrerer Dateien gleichzeitig",
            "  ✓  Textbearbeitung direkt im Editor",
        ]:
            add_row(c3, line, top=2, bottom=2)
        add_gap(c3, 8)

        # ── 4. OCR-Hinweis ────────────────────────────────────────────
        c4 = make_card("🔍  OCR – Texterkennung in Bildern")
        add_row(c4, "Für Bilder und gescannte PDFs wird Tesseract OCR")
        add_row(c4, "verwendet  (Open-Source, lokal – keine Cloud).")
        add_gap(c4, 4)
        add_row(c4, "  Sprachen:   Deutsch + Englisch")
        add_row(c4, "  Engine:     Tesseract 5.x")
        add_gap(c4, 4)
        add_row(c4, "Tipp: Bessere Bildqualität = bessere Erkennung.")
        add_row(c4, "Empfehlung: mind. 150 DPI, guter Kontrast.")
        add_gap(c4, 8)

        # ── 5. Bedienung ──────────────────────────────────────────────
        c5 = make_card("🖱️  Bedienung")
        add_row(c5, "  1.  Datei auswählen  (Button oder Drag & Drop)")
        add_row(c5, "  2.  Text wird automatisch erkannt und angezeigt")
        add_row(c5, "  3.  Text im Editor prüfen")
        add_row(c5, "  4.  »Alles kopieren«  ·  »Speichern (TXT)«  ·  PRO: DOCX/PDF")
        add_gap(c5, 8)

        # ── 6. Über / Firma ───────────────────────────────────────────
        c6 = make_card(f"ℹ️  Über  {APP_NAME}")
        add_row(c6, f"  Version:          {APP_VERSION}")
        add_row(c6, f"  Entwickelt von:   {COMPANY_NAME}")
        add_row(c6, f"  Website:          {COMPANY_WEBSITE}")
        add_row(c6, f"  E-Mail:           {COMPANY_EMAIL}")
        add_gap(c6, 4)
        add_row(c6, f"  {COPYRIGHT}", top=0, bottom=2)
        add_gap(c6, 8)

        # Abstand unten
        ctk.CTkFrame(sf, height=10, fg_color="transparent").grid()

        # ── Footer-Button ─────────────────────────────────────────────
        foot = ctk.CTkFrame(self, fg_color=(LIGHT_BG, DARK_BG), corner_radius=0)
        foot.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        foot.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            foot, text="Schließen",
            width=130, height=34,
            font=ctk.CTkFont(family=FONT, size=13),
            fg_color=NAVY, hover_color="#1a3a5c",
            corner_radius=8,
            command=self.destroy,
        ).grid(row=0, column=0, pady=14)
