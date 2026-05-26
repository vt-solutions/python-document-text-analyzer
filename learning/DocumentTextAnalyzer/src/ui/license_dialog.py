"""
license_dialog.py
Lizenzaktivierungs-Dialog fuer VT Document Text Converter.
Breites, professionelles 2-Spalten-Layout.
"""

import os
import sys
import tkinter as tk
import customtkinter as ctk
from PIL import Image

from src.version import (
    APP_NAME, APP_VERSION,
    COMPANY_NAME, COMPANY_EMAIL, COMPANY_WEBSITE,
    COPYRIGHT, LOGO_PATH, ICON_PATH,
)
import src.licensing.license_manager as lm

# ── Farben ────────────────────────────────────────────────────────────
FONT        = "Segoe UI"
NAVY_DARK   = "#0d1f35"
NAVY_MED    = "#102a47"
BLUE_ACCENT = "#1e5fd4"
BLUE_HOVER  = "#1a4fa8"
LIGHT_BG    = "#f0f2f5"
DARK_BG     = "#0f1c2e"
CARD_L      = "#ffffff"
CARD_D      = "#132030"
SEP_L       = "#dce3ec"
SEP_D       = "#1e3a5a"
WHITE       = "#ffffff"
SUCCESS     = "#16a34a"
ERROR_RED   = "#dc2626"
GREEN_CARD_D = "#0a2818"
GREEN_CARD_L = "#f0faf4"


class LicenseDialog(tk.Toplevel):
    """
    Modaler Lizenzaktivierungs-Dialog – breites 2-Spalten-Layout.
    result: "activated" | "trial" | None (→ App beenden)
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.result: str | None = None
        self._is_dark = ctk.get_appearance_mode() == "Dark"

        self.configure(bg=NAVY_DARK)
        self.title(f"Lizenzaktivierung  –  {APP_NAME}")
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.resizable(True, True)

        # Icon
        _base = (sys._MEIPASS if hasattr(sys, "_MEIPASS")
                 else os.path.normpath(
                     os.path.join(os.path.dirname(__file__), "..", "..")))
        ico = os.path.join(_base, ICON_PATH)
        if os.path.isfile(ico):
            try:
                self.iconbitmap(ico)
            except Exception:
                pass

        # Fenstergroesse: 1800x1050, an Bildschirm anpassen
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        dw = min(1800, sw - 40)
        dh = min(1300, sh - 60)
        x  = max(0, (sw - dw) // 2)
        y  = max(0, (sh - dh) // 2)
        self.geometry(f"{dw}x{dh}+{x}+{y}")
        self.minsize(1400, 900)

        self._build_ui()
        self.after(80, self._make_modal)

    def _make_modal(self):
        try:
            self.grab_set()
            self.focus_force()
            self.lift()
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  UI                                                                  #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        dark = self._is_dark

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)   # Content wächst

        # ── Header ───────────────────────────────────────────────────
        self._build_header()

        # ── Hauptinhalt (2 Spalten) ───────────────────────────────────
        self._build_content()

        # ── Footer ───────────────────────────────────────────────────
        self._build_footer()

    # ─── HEADER ────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = tk.Frame(self, bg=NAVY_DARK)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_columnconfigure(1, weight=1)

        # Logo links
        _base = (sys._MEIPASS if hasattr(sys, "_MEIPASS")
                 else os.path.normpath(
                     os.path.join(os.path.dirname(__file__), "..", "..")))
        logo_path = os.path.join(_base, LOGO_PATH)
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
                sc = min(240 / ow, 64 / oh)
                self._logo = ctk.CTkImage(
                    light_image=pil_inv, dark_image=pil_inv,
                    size=(int(ow * sc), int(oh * sc)))
                ctk.CTkLabel(
                    hdr, image=self._logo, text="", bg_color=NAVY_DARK,
                ).grid(row=0, column=0, rowspan=2, padx=(48, 32), pady=22)
            except Exception:
                tk.Label(hdr, text=COMPANY_NAME, font=(FONT, 13, "bold"),
                         fg=WHITE, bg=NAVY_DARK).grid(
                    row=0, column=0, rowspan=2, padx=(48, 32), pady=22)
        else:
            tk.Label(hdr, text=COMPANY_NAME, font=(FONT, 13, "bold"),
                     fg=WHITE, bg=NAVY_DARK).grid(
                row=0, column=0, rowspan=2, padx=(48, 32), pady=22)

        # Begrüßung rechts vom Logo
        tk.Label(hdr, text=f"Willkommen bei  {APP_NAME}",
                 font=(FONT, 20, "bold"),
                 fg=WHITE, bg=NAVY_DARK,
                 anchor="w").grid(row=0, column=1, sticky="w", pady=(22, 4))

        tk.Label(hdr,
                 text="Aktivieren Sie Ihre Lizenz oder starten Sie die kostenlose 30-Tage-Testversion.",
                 font=(FONT, 12),
                 fg="#6b8caa", bg=NAVY_DARK,
                 anchor="w").grid(row=1, column=1, sticky="w", pady=(0, 22))

        # Trennlinie
        tk.Frame(self, bg=SEP_D, height=1).grid(row=0, column=0, sticky="sew")

    # ─── CONTENT ───────────────────────────────────────────────────────

    def _build_content(self):
        dark   = self._is_dark
        bg     = DARK_BG if dark else LIGHT_BG

        outer = ctk.CTkFrame(self, fg_color=(LIGHT_BG, DARK_BG), corner_radius=0)
        outer.grid(row=1, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=55)   # Linke Spalte: Formular (55 %)
        outer.grid_columnconfigure(1, weight=45)   # Rechte Spalte: Trial  (45 %)
        outer.grid_rowconfigure(0, weight=1)

        # ── Linke Spalte: Lizenz aktivieren ──────────────────────────
        left = ctk.CTkFrame(outer, fg_color=(CARD_L, CARD_D), corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        left.grid_columnconfigure(0, weight=1)

        # Abstandshalter oben
        ctk.CTkFrame(left, height=36, fg_color="transparent").grid()

        ctk.CTkLabel(
            left, text="🔑  Lizenz aktivieren",
            font=ctk.CTkFont(family=FONT, size=17, weight="bold"),
            text_color=(NAVY_DARK, WHITE), anchor="w",
        ).grid(sticky="w", padx=52, pady=(0, 4))

        ctk.CTkFrame(left, height=1, fg_color=(SEP_L, SEP_D)).grid(
            sticky="ew", padx=52, pady=(0, 20))

        # Firmenname
        ctk.CTkLabel(
            left, text="Firmenname",
            font=ctk.CTkFont(family=FONT, size=13, weight="bold"),
            text_color=("#334155", "#8aa0bc"), anchor="w",
        ).grid(sticky="w", padx=52, pady=(0, 6))

        self.ent_customer = ctk.CTkEntry(
            left,
            placeholder_text="z. B.  Mustermann GmbH",
            height=46,
            font=ctk.CTkFont(family=FONT, size=14),
            fg_color=(CARD_L, "#0d2035"),
            border_color=(SEP_L, "#2a4a6a"),
            border_width=1,
            text_color=(NAVY_DARK, "#d0e0f0"),
            placeholder_text_color=("#9aaabb", "#4a6a8a"),
            corner_radius=8,
        )
        self.ent_customer.grid(sticky="ew", padx=52, pady=(0, 22))

        # Lizenzschlüssel
        ctk.CTkLabel(
            left, text="Lizenzschlüssel",
            font=ctk.CTkFont(family=FONT, size=13, weight="bold"),
            text_color=("#334155", "#8aa0bc"), anchor="w",
        ).grid(sticky="w", padx=52, pady=(0, 6))

        self.ent_key = ctk.CTkEntry(
            left,
            placeholder_text="VT-YYYY-XXXX-XXXX",
            height=46,
            font=ctk.CTkFont(family=FONT, size=14),
            fg_color=(CARD_L, "#0d2035"),
            border_color=(SEP_L, "#2a4a6a"),
            border_width=1,
            text_color=(NAVY_DARK, "#d0e0f0"),
            placeholder_text_color=("#9aaabb", "#4a6a8a"),
            corner_radius=8,
        )
        self.ent_key.grid(sticky="ew", padx=52, pady=(0, 6))

        ctk.CTkLabel(
            left,
            text="Format: VT-YYYY-XXXX-XXXX  (Beispiel: VT-2026-ABCD-1234)",
            font=ctk.CTkFont(family=FONT, size=11),
            text_color=("#7a8a9a", "#4a6a8a"), anchor="w",
        ).grid(sticky="w", padx=52, pady=(0, 6))

        # Statuszeile
        self.lbl_status = ctk.CTkLabel(
            left, text="",
            font=ctk.CTkFont(family=FONT, size=12),
            text_color=(ERROR_RED, "#ff6b6b"),
            anchor="w", justify="left",
        )
        self.lbl_status.grid(sticky="w", padx=52, pady=(0, 6))

        # Aktivieren-Button
        self.btn_activate = ctk.CTkButton(
            left,
            text="🔑  Lizenz aktivieren",
            height=50,
            font=ctk.CTkFont(family=FONT, size=15, weight="bold"),
            fg_color=BLUE_ACCENT, hover_color=BLUE_HOVER,
            text_color=WHITE, corner_radius=8,
            command=self._on_activate,
        )
        self.btn_activate.grid(sticky="ew", padx=52, pady=(8, 32))

        # ── Vertikaler Trenner ────────────────────────────────────────
        tk.Frame(outer, bg=SEP_D, width=1).grid(
            row=0, column=0, sticky="nse", padx=0)

        # ── Rechte Spalte: Testversion ────────────────────────────────
        right_bg = (GREEN_CARD_L, "#0a1e12") if False else (LIGHT_BG, DARK_BG)
        right = ctk.CTkFrame(outer, fg_color=(LIGHT_BG, DARK_BG), corner_radius=0)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        ctk.CTkFrame(right, height=24, fg_color="transparent").grid()

        ctk.CTkLabel(
            right, text="▶  Testversion starten",
            font=ctk.CTkFont(family=FONT, size=17, weight="bold"),
            text_color=(NAVY_DARK, WHITE), anchor="w",
        ).grid(sticky="w", padx=52, pady=(0, 4))

        ctk.CTkFrame(right, height=1, fg_color=(SEP_L, SEP_D)).grid(
            sticky="ew", padx=52, pady=(0, 20))

        ctk.CTkLabel(
            right,
            text="Noch kein Lizenzschlüssel? Kein Problem.",
            font=ctk.CTkFont(family=FONT, size=13, weight="bold"),
            text_color=(NAVY_DARK, "#c8daf0"), anchor="w",
        ).grid(sticky="w", padx=52, pady=(0, 8))

        ctk.CTkLabel(
            right,
            text=(
                "Testen Sie alle Funktionen des\n"
                "VT Document Text Converters\n"
                "30 Tage lang vollständig kostenlos.\n\n"
                "Keine Kreditkarte erforderlich.\n"
                "Keine versteckten Kosten.\n"
                "Jederzeit auf PRO upgraden."
            ),
            font=ctk.CTkFont(family=FONT, size=12),
            text_color=("#4a5568", "#8aa0bc"),
            anchor="w", justify="left",
        ).grid(sticky="w", padx=52, pady=(0, 20))

        # Vorteile
        for check_text in [
            "✓  Alle Dateiformate  (PDF, Word, Excel, Bilder …)",
            "✓  OCR-Texterkennung  (Deutsch + Englisch)",
            "✓  30 Tage – vollständige Funktionen",
            "✓  100 % lokal – keine Cloud",
        ]:
            ctk.CTkLabel(
                right, text=check_text,
                font=ctk.CTkFont(family=FONT, size=12),
                text_color=(SUCCESS, "#4ade80"),
                anchor="w",
            ).grid(sticky="w", padx=52, pady=(0, 4))

        ctk.CTkFrame(right, height=20, fg_color="transparent").grid()

        self.btn_trial = ctk.CTkButton(
            right,
            text="▶  30-Tage-Testversion starten",
            height=50,
            font=ctk.CTkFont(family=FONT, size=15, weight="bold"),
            fg_color=(NAVY_DARK, NAVY_MED),
            hover_color=(NAVY_MED, "#1a4a6a"),
            text_color=WHITE,
            border_width=1,
            border_color=(BLUE_ACCENT, BLUE_ACCENT),
            corner_radius=8,
            command=self._on_trial,
        )
        self.btn_trial.grid(sticky="ew", padx=52, pady=(0, 32))

    # ─── FOOTER ────────────────────────────────────────────────────────

    def _build_footer(self):
        tk.Frame(self, bg=SEP_D, height=1).grid(row=2, column=0, sticky="ew")

        foot = tk.Frame(self, bg=NAVY_DARK)
        foot.grid(row=3, column=0, sticky="ew")
        foot.grid_columnconfigure(0, weight=1)
        foot.grid_columnconfigure(1, weight=0)

        tk.Label(
            foot,
            text=f"{COMPANY_NAME}  ·  {COMPANY_EMAIL}  ·  {COMPANY_WEBSITE}",
            font=(FONT, 11), fg="#4a6a8a", bg=NAVY_DARK, anchor="w",
        ).grid(row=0, column=0, padx=48, pady=14, sticky="w")

        tk.Label(
            foot,
            text=f"Version {APP_VERSION}",
            font=(FONT, 11), fg="#4a6a8a", bg=NAVY_DARK, anchor="e",
        ).grid(row=0, column=1, padx=48, pady=14, sticky="e")

    # ------------------------------------------------------------------ #
    #  Button-Handler                                                      #
    # ------------------------------------------------------------------ #

    def _set_status(self, text: str, color: str):
        self.lbl_status.configure(text=text, text_color=color)

    def _on_activate(self):
        customer = self.ent_customer.get().strip()
        key      = self.ent_key.get().strip()

        if not customer:
            self._set_status("⚠  Bitte Firmennamen eingeben.", ERROR_RED)
            self.ent_customer.focus_set()
            return
        if not key:
            self._set_status("⚠  Bitte Lizenzschlüssel eingeben.", ERROR_RED)
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
            self._set_status(f"⚠  {msg.splitlines()[0]}", ERROR_RED)
            self.btn_activate.configure(text="🔑  Lizenz aktivieren", state="normal")

    def _on_trial(self):
        lm.start_trial()
        self.result = "trial"
        self.destroy()

    def _on_close(self):
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
