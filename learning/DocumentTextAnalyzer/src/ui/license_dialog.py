"""
license_dialog.py  –  VT Document Text Converter
Lizenzaktivierungs-Dialog, breites 2-Spalten-Layout.
"""

import os
import sys
import tkinter as tk
import customtkinter as ctk
from datetime import datetime
from PIL import Image

from src.version import (
    APP_NAME, APP_VERSION,
    COMPANY_NAME, COMPANY_EMAIL, COMPANY_WEBSITE,
    LOGO_PATH, ICON_PATH,
)
import src.licensing.license_manager as lm

from src.theme import (
    FONT_FAMILY as FONT,
    FONT_TITLE, FONT_SECTION, FONT_LABEL, FONT_BODY,
    FONT_INPUT, FONT_BUTTON, FONT_SUBTITLE, FONT_HINT, FONT_FOOTER,
    HEIGHT_BUTTON, HEIGHT_ENTRY,
    NAVY_DARK, NAVY_MED, BLUE_ACCENT, BLUE_HOVER, WHITE,
    LIGHT_BG, LIGHT_CARD as CARD_L, DARK_BG, DARK_CARD as CARD_D,
    SEP_LIGHT as SEP_L, SEP_DARK as SEP_D, SUCCESS, ERROR_RED,
)

# Zweite Dunkel-Kartenhintergrundfarbe (nur im Dialog genutzt)
CARD_D2 = "#0e1a29"


class LicenseDialog(tk.Toplevel):
    """
    result: "activated" | "trial" | None  (None → App soll beenden)
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.result: str | None = None
        self._is_dark = ctk.get_appearance_mode() == "Dark"

        # Fensterkonfiguration
        self.title(f"Lizenzaktivierung  –  {APP_NAME}")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        bg = DARK_BG if self._is_dark else LIGHT_BG
        self.configure(bg=bg)

        # App-Icon
        _base = (sys._MEIPASS if hasattr(sys, "_MEIPASS")
                 else os.path.normpath(
                     os.path.join(os.path.dirname(__file__), "..", "..")))
        ico = os.path.join(_base, ICON_PATH)
        if os.path.isfile(ico):
            try:
                self.iconbitmap(ico)
            except Exception:
                pass

        # Fenstergröße: max 1800×1300, an Bildschirm anpassen
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        dw = min(1800, sw - 40)
        dh = min(1300, sh - 60)
        self.geometry(f"{dw}x{dh}+{max(0,(sw-dw)//2)}+{max(0,(sh-dh)//2)}")
        self.minsize(min(900, sw - 40), min(660, sh - 60))

        self._build_ui()
        self.after(100, self._make_modal)

    # ------------------------------------------------------------------ #
    #  Modal                                                               #
    # ------------------------------------------------------------------ #

    def _make_modal(self):
        try:
            self.grab_set()
            self.focus_force()
            self.lift()
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  UI-Aufbau                                                           #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        # Hauptstruktur: Header | Content | Footer  (pack, top-to-bottom)
        self._build_header()
        self._build_content()
        self._build_footer()

    # ── HEADER ─────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self, bg=NAVY_DARK)
        hdr.pack(side="top", fill="x")

        # Inhalt des Headers mit pack (horizontal)
        inner = tk.Frame(hdr, bg=NAVY_DARK)
        inner.pack(fill="x", padx=36, pady=(14, 14))

        # Logo links
        _base = (sys._MEIPASS if hasattr(sys, "_MEIPASS")
                 else os.path.normpath(
                     os.path.join(os.path.dirname(__file__), "..", "..")))
        logo_path = os.path.join(_base, LOGO_PATH)
        logo_placed = False
        if os.path.isfile(logo_path):
            try:
                pil = Image.open(logo_path).convert("RGBA")
                r, g, b, a = pil.split()
                pil_inv = Image.merge("RGBA", (
                    r.point(lambda v: 255 - v),
                    g.point(lambda v: 255 - v),
                    b.point(lambda v: 255 - v), a,
                ))
                ow, oh = pil_inv.size
                sc = min(170 / ow, 46 / oh)
                self._logo = ctk.CTkImage(
                    light_image=pil_inv, dark_image=pil_inv,
                    size=(int(ow * sc), int(oh * sc)))
                lbl_logo = ctk.CTkLabel(
                    inner, image=self._logo, text="", bg_color=NAVY_DARK)
                lbl_logo.pack(side="left", padx=(0, 36))
                logo_placed = True
            except Exception:
                pass

        if not logo_placed:
            tk.Label(inner, text=COMPANY_NAME,
                     font=(FONT, FONT_SECTION, "bold"), fg=WHITE, bg=NAVY_DARK
                     ).pack(side="left", padx=(0, 36))

        # Texte rechts vom Logo
        txt_frame = tk.Frame(inner, bg=NAVY_DARK)
        txt_frame.pack(side="left", fill="both", expand=True)

        tk.Label(txt_frame,
                 text=f"Willkommen bei  {APP_NAME}",
                 font=(FONT, FONT_TITLE, "bold"),
                 fg=WHITE, bg=NAVY_DARK, anchor="w",
                 ).pack(anchor="w", pady=(2, 2))

        tk.Label(txt_frame,
                 text="Aktivieren Sie Ihre Lizenz oder starten Sie die kostenlose 30-Tage-Testversion.",
                 font=(FONT, FONT_SUBTITLE),
                 fg="#6b8caa", bg=NAVY_DARK, anchor="w",
                 ).pack(anchor="w")

        # Trennlinie unten am Header
        tk.Frame(self, bg=SEP_D, height=1).pack(side="top", fill="x")

    # ── CONTENT  (2 Spalten mit pack) ──────────────────────────────────

    def _build_content(self):
        dark = self._is_dark
        bg   = DARK_BG if dark else LIGHT_BG

        # Container für beide Spalten
        content = tk.Frame(self, bg=bg)
        content.pack(side="top", fill="both", expand=True)

        # ── Linke Spalte ──────────────────────────────────────────────
        left_bg = CARD_D if dark else CARD_L
        left = tk.Frame(content, bg=left_bg)
        left.pack(side="left", fill="both", expand=True)

        # Vertikaler Trenner
        tk.Frame(content, bg=SEP_D, width=1).pack(side="left", fill="y")

        # ── Rechte Spalte ─────────────────────────────────────────────
        right_bg = CARD_D2 if dark else "#f8fafc"
        right = tk.Frame(content, bg=right_bg)
        right.pack(side="left", fill="both", expand=True)

        # Inhalte der Spalten befüllen
        self._fill_left(left, dark)
        self._fill_right(right, dark)

    # ── LINKE SPALTE: Lizenz aktivieren ────────────────────────────────

    def _fill_left(self, parent, dark):
        txt   = WHITE if dark else NAVY_DARK
        muted = "#8aa0bc" if dark else "#334155"
        hint  = "#4a6a8a" if dark else "#7a8a9a"
        bg    = CARD_D   if dark else CARD_L

        pad = 36   # Innenabstand links/rechts

        tk.Frame(parent, bg=bg, height=20).pack(fill="x")

        # Abschnittstitel
        tk.Label(parent, text="🔑  Lizenz aktivieren",
                 font=(FONT, FONT_SECTION, "bold"),
                 fg=txt, bg=bg, anchor="w",
                 ).pack(fill="x", padx=pad)

        tk.Frame(parent, bg=SEP_D if dark else SEP_L,
                 height=1).pack(fill="x", padx=pad, pady=(8, 24))

        # Benutzername
        tk.Label(parent, text="Benutzername",
                 font=(FONT, FONT_LABEL, "bold"),
                 fg=muted, bg=bg, anchor="w",
                 ).pack(fill="x", padx=pad, pady=(0, 4))

        self.ent_customer = ctk.CTkEntry(
            parent,
            placeholder_text="z. B.  Max Mustermann",
            height=HEIGHT_ENTRY,
            font=ctk.CTkFont(family=FONT, size=FONT_INPUT),
            fg_color=(CARD_L, "#0d2035"),
            border_color=(SEP_L, "#2a4a6a"),
            border_width=1,
            text_color=(NAVY_DARK, "#d0e0f0"),
            placeholder_text_color=("#9aaabb", "#4a6a8a"),
            corner_radius=8,
        )
        self.ent_customer.pack(fill="x", padx=pad, pady=(0, 24))

        # Lizenzschlüssel
        tk.Label(parent, text="Lizenzschlüssel",
                 font=(FONT, FONT_LABEL, "bold"),
                 fg=muted, bg=bg, anchor="w",
                 ).pack(fill="x", padx=pad, pady=(0, 4))

        self.ent_key = ctk.CTkEntry(
            parent,
            placeholder_text="VT-YYYY-XXXX-XXXX",
            height=HEIGHT_ENTRY,
            font=ctk.CTkFont(family=FONT, size=FONT_INPUT),
            fg_color=(CARD_L, "#0d2035"),
            border_color=(SEP_L, "#2a4a6a"),
            border_width=1,
            text_color=(NAVY_DARK, "#d0e0f0"),
            placeholder_text_color=("#9aaabb", "#4a6a8a"),
            corner_radius=8,
        )
        self.ent_key.pack(fill="x", padx=pad, pady=(0, 6))

        tk.Label(parent,
                 text="Format: VT-YYYY-XXXX-XXXX  (Beispiel: VT-2026-ABCD-1234)",
                 font=(FONT, FONT_HINT), fg=hint, bg=bg, anchor="w",
                 ).pack(fill="x", padx=pad, pady=(0, 4))

        # Statuszeile
        self.lbl_status = tk.Label(
            parent, text="",
            font=(FONT, FONT_BODY), fg=ERROR_RED, bg=bg, anchor="w", justify="left",
        )
        self.lbl_status.pack(fill="x", padx=pad, pady=(0, 4))

        # Aktivieren-Button
        self.btn_activate = ctk.CTkButton(
            parent,
            text="🔑  Lizenz aktivieren",
            height=HEIGHT_BUTTON,
            font=ctk.CTkFont(family=FONT, size=FONT_BUTTON, weight="bold"),
            fg_color=BLUE_ACCENT, hover_color=BLUE_HOVER,
            text_color=WHITE, corner_radius=8,
            command=self._on_activate,
        )
        self.btn_activate.pack(fill="x", padx=pad, pady=(8, 16))

        tk.Frame(parent, bg=bg, height=32).pack(fill="x")

    # ── RECHTE SPALTE: Testversion ──────────────────────────────────────

    def _fill_right(self, parent, dark):
        txt    = WHITE if dark else NAVY_DARK
        muted  = "#8aa0bc" if dark else "#4a5568"
        bg     = CARD_D2 if dark else "#f8fafc"

        pad = 36

        tk.Frame(parent, bg=bg, height=20).pack(fill="x")

        # Abschnittstitel
        tk.Label(parent, text="▶  Testversion starten",
                 font=(FONT, FONT_SECTION, "bold"),
                 fg=txt, bg=bg, anchor="w",
                 ).pack(fill="x", padx=pad)

        tk.Frame(parent, bg=SEP_D if dark else SEP_D,
                 height=1).pack(fill="x", padx=pad, pady=(8, 24))

        tk.Label(parent,
                 text="Noch kein Lizenzschlüssel? Kein Problem.",
                 font=(FONT, FONT_LABEL, "bold"),
                 fg=txt, bg=bg, anchor="w",
                 ).pack(fill="x", padx=pad, pady=(0, 10))

        tk.Label(parent,
                 text=(
                     "Testen Sie alle Funktionen des VT Document Text Converters\n"
                     "30 Tage lang vollständig kostenlos.\n\n"
                     "Keine Kreditkarte erforderlich.\n"
                     "Keine versteckten Kosten.\n"
                     "Jederzeit auf PRO upgraden."
                 ),
                 font=(FONT, FONT_BODY),
                 fg=muted, bg=bg, anchor="w", justify="left",
                 ).pack(fill="x", padx=pad, pady=(0, 14))

        # Vorteile
        for line in [
            "✓   Alle Dateiformate  (PDF, Word, Excel, Bilder …)",
            "✓   OCR-Texterkennung  (Deutsch + Englisch)",
            "✓   30 Tage – vollständige Funktionen",
            "✓   100 % lokal – keine Cloud",
        ]:
            tk.Label(parent, text=line,
                     font=(FONT, FONT_BODY),
                     fg="#4ade80", bg=bg, anchor="w",
                     ).pack(fill="x", padx=pad, pady=(0, 3))

        tk.Frame(parent, bg=bg, height=20).pack(fill="x")

        # ── Trial-Status ermitteln ─────────────────────────────────
        _data         = lm.load()
        _is_activated = lm.is_activated()
        _is_expired   = lm.is_trial_expired()
        _trial_active = (
            _data.get("edition") == "TRIAL"
            and not _is_expired
            and not _is_activated
        )

        # Status-Box anzeigen wenn nötig
        if _trial_active or _is_expired:
            if _trial_active:
                try:
                    ends      = datetime.fromisoformat(_data.get("trial_ends", ""))
                    remaining = max(0, (ends - datetime.now()).days)
                    ends_str  = ends.strftime("%d.%m.%Y")
                    msg = (f"Sie nutzen bereits eine Testversion.\n"
                           f"Noch  {remaining}  Tage verbleibend  (bis {ends_str}).")
                    box_bg  = "#2a1a00" if dark else "#fff8ed"
                    box_fg  = "#fbbf24"
                    box_brd = "#7a5010" if dark else "#f0c060"
                except Exception:
                    msg     = "Sie nutzen bereits eine Testversion."
                    box_bg  = "#2a1a00" if dark else "#fff8ed"
                    box_fg  = "#fbbf24"
                    box_brd = "#7a5010" if dark else "#f0c060"
            else:
                msg     = "Die Testversion ist abgelaufen.\nBitte aktivieren Sie eine Lizenz."
                box_bg  = "#2a0a0a" if dark else "#fef2f2"
                box_fg  = "#f87171"
                box_brd = "#7a2020" if dark else "#f0a0a0"

            box = tk.Frame(parent, bg=box_bg,
                           highlightbackground=box_brd,
                           highlightthickness=1)
            box.pack(fill="x", padx=pad, pady=(0, 20))

            tk.Label(box, text=msg,
                     font=(FONT, FONT_BODY),
                     fg=box_fg, bg=box_bg,
                     anchor="w", justify="left",
                     ).pack(anchor="w", padx=16, pady=14)

        # Button-Zustand
        if _trial_active:
            btn_text  = "✓  Testversion läuft bereits"
            btn_state = "disabled"
        elif _is_expired:
            btn_text  = "✗  Testversion abgelaufen"
            btn_state = "disabled"
        else:
            btn_text  = "▶  30-Tage-Testversion starten"
            btn_state = "normal"

        self.btn_trial = ctk.CTkButton(
            parent,
            text=btn_text,
            height=HEIGHT_BUTTON,
            font=ctk.CTkFont(family=FONT, size=FONT_BUTTON, weight="bold"),
            fg_color=(NAVY_DARK, NAVY_MED),
            hover_color=(NAVY_MED, "#1a4a6a"),
            text_color=WHITE,
            border_width=1,
            border_color=(BLUE_ACCENT, BLUE_ACCENT),
            corner_radius=8,
            state=btn_state,
            command=self._on_trial,
        )
        self.btn_trial.pack(fill="x", padx=pad, pady=(0, 32))

    # ── FOOTER ─────────────────────────────────────────────────────────

    def _build_footer(self):
        tk.Frame(self, bg=SEP_D, height=1).pack(side="bottom", fill="x")

        foot = tk.Frame(self, bg=NAVY_DARK)
        foot.pack(side="bottom", fill="x")

        tk.Label(foot,
                 text=f"{COMPANY_NAME}  ·  {COMPANY_EMAIL}  ·  {COMPANY_WEBSITE}",
                 font=(FONT, FONT_FOOTER), fg="#4a6a8a", bg=NAVY_DARK, anchor="w",
                 ).pack(side="left", padx=36, pady=10)

        tk.Label(foot,
                 text=f"Version {APP_VERSION}",
                 font=(FONT, FONT_FOOTER), fg="#4a6a8a", bg=NAVY_DARK, anchor="e",
                 ).pack(side="right", padx=36, pady=10)

    # ------------------------------------------------------------------ #
    #  Handler                                                             #
    # ------------------------------------------------------------------ #

    def _set_status(self, text: str, color: str = ERROR_RED):
        self.lbl_status.configure(fg=color, text=text)

    def _on_activate(self):
        customer = self.ent_customer.get().strip()
        key      = self.ent_key.get().strip()

        if not customer:
            self._set_status("⚠  Bitte Benutzernamen eingeben.")
            self.ent_customer.focus_set()
            return
        if not key:
            self._set_status("⚠  Bitte Lizenzschlüssel eingeben.")
            self.ent_key.focus_set()
            return

        self.btn_activate.configure(text="⏳  Wird geprüft …", state="disabled")
        self.update()

        ok, msg = lm.activate(customer, key)

        if ok:
            self._set_status(f"✓  {msg.splitlines()[0]}", SUCCESS)
            self.btn_activate.configure(
                text="✓  Aktiviert!",
                fg_color=(SUCCESS, SUCCESS),
                hover_color=(SUCCESS, SUCCESS),
            )
            self.result = "activated"
            self.after(1200, self.destroy)
        else:
            self._set_status(f"⚠  {msg.splitlines()[0]}")
            self.btn_activate.configure(text="🔑  Lizenz aktivieren", state="normal")

    def _on_trial(self):
        lm.start_trial()
        self.result = "trial"
        self.destroy()

    def _on_quit(self):
        """Anwendung sofort sauber beenden."""
        self.result = None
        self.destroy()
        try:
            self.master.destroy()
        except Exception:
            pass
        sys.exit(0)

    def _on_close(self):
        """Fenster-X gedrückt → App beenden."""
        self.result = None
        self.destroy()


# ── Standalone-Test ───────────────────────────────────────────────────
if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    root = ctk.CTk()
    root.withdraw()
    dlg = LicenseDialog(root)
    root.wait_window(dlg)
    print(f"Ergebnis: {dlg.result}")
    root.destroy()
