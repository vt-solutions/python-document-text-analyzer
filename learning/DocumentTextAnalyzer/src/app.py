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

from src.file_router import route_file, ALL_SUPPORTED_EXTS, _PRO_EXTS
from src.ui.info_dialog import InfoDialog
from src.settings_manager import load as load_settings, save as save_settings
import src.licensing.license_manager as lm
from src.version import (
    APP_NAME, APP_VERSION,
    COMPANY_NAME, COMPANY_EMAIL, COMPANY_WEBSITE,
    LOGO_PATH, ICON_PATH,
)
from src.theme import (
    FONT_FAMILY,
    FONT_TITLE, FONT_SECTION, FONT_LABEL, FONT_BODY,
    FONT_INPUT, FONT_BUTTON, FONT_SUBTITLE, FONT_HINT, FONT_FOOTER, FONT_STATUS,
    HEIGHT_BUTTON, HEIGHT_ENTRY,
    NAVY_DARK, NAVY_MED, BLUE_ACCENT, WHITE,
    LIGHT_BG, LIGHT_CARD, DARK_BG, DARK_CARD,
    TEXT_MUTED, SEP_LIGHT, SEP_DARK, SUCCESS, ERROR_RED,
)

THEME_LIGHT = "☀  Hellmodus"
THEME_DARK  = "🌙  Dunkelmodus"

_saved = load_settings()
ctk.set_appearance_mode(_saved.get("theme", "Dark"))
ctk.set_default_color_theme("blue")

_STD_EXTS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp",
    ".docx", ".xlsx", ".pptx"
}


class DocumentTextAnalyzerApp(TkinterDnD.Tk):
    """Hauptfenster im vt-solutions Corporate Design."""

    def __init__(self):
        super().__init__()

        _needs_license = lm.is_first_run() or lm.is_trial_expired()
        if _needs_license:
            self.withdraw()

        self.title(APP_NAME)
        self.minsize(920, 680)

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w  = min(1800, sw - 40)
        h  = min(1050, sh - 80)
        x  = (sw - w) // 2
        y  = (sh - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._selected_file = ""
        self._is_dark = (_saved.get("theme", "Dark") == "Dark")
        self._edit_mode = False   # PRO: Textbearbeitung
        self.configure(bg=DARK_BG if self._is_dark else LIGHT_BG)

        self._set_window_icon()
        self._build_ui()
        self._setup_drag_and_drop()

        if _needs_license:
            self.after(60, self._check_license_on_startup)

    # ------------------------------------------------------------------ #
    #  Hilfsmethoden                                                      #
    # ------------------------------------------------------------------ #

    def _is_pro(self) -> bool:
        return lm.has_feature("extra_formats")   # PRO-Guard

    def _supported_exts(self) -> set[str]:
        return ALL_SUPPORTED_EXTS if self._is_pro() else _STD_EXTS

    def _pro_guard(self, feature_label: str) -> bool:
        """Zeigt einen Hinweis wenn kein PRO-Zugang. Gibt True zurück wenn PRO."""
        if self._is_pro():
            return True
        messagebox.showinfo(
            "PRO-Feature",
            f"„{feature_label}" ist nur in der PRO-Version verfügbar.\n\n"
            "Upgraden Sie auf VT Document Text Converter PRO,\n"
            "um dieses Feature zu nutzen.",
            parent=self,
        )
        return False

    # ------------------------------------------------------------------ #
    #  Icon                                                               #
    # ------------------------------------------------------------------ #

    def _set_window_icon(self):
        import sys
        base = (sys._MEIPASS
                if hasattr(sys, "_MEIPASS")
                else os.path.normpath(
                    os.path.join(os.path.abspath(os.path.dirname(__file__)), "..")
                ))
        ico_path = os.path.abspath(os.path.join(base, ICON_PATH))
        if not os.path.isfile(ico_path):
            return
        try:
            self.iconbitmap(ico_path)
        except Exception:
            pass
        self.after(150, lambda p=ico_path: self._apply_taskbar_icon(p))

    def _apply_taskbar_icon(self, ico_path: str):
        try:
            import ctypes
            user32 = ctypes.windll.user32
            IMAGE_ICON      = 1
            LR_LOADFROMFILE = 0x0010
            LR_DEFAULTSIZE  = 0x0040
            WM_SETICON      = 0x0080
            ICON_SMALL      = 0
            ICON_BIG        = 1
            GA_ROOT         = 2
            h_big   = user32.LoadImageW(None, ico_path, IMAGE_ICON, 0, 0,
                                        LR_LOADFROMFILE | LR_DEFAULTSIZE)
            h_small = user32.LoadImageW(None, ico_path, IMAGE_ICON, 16, 16,
                                        LR_LOADFROMFILE)
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
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        self._build_menubar()
        self._build_header()
        self._build_content()
        self._build_footer()

    # ---- MENÜLEISTE -------------------------------------------------------

    def _build_menubar(self):
        dark    = self._is_dark
        menu_bg = "#132030" if dark else "#ffffff"
        menu_fg = "#e8eaf0" if dark else NAVY_DARK
        act_bg  = BLUE_ACCENT
        act_fg  = "#ffffff"

        kw = dict(
            tearoff=0,
            bg=menu_bg, fg=menu_fg,
            activebackground=act_bg, activeforeground=act_fg,
            font=(FONT_FAMILY, 10),
            relief="flat", bd=1,
        )

        menubar = tk.Menu(self, **kw)

        # ── Datei ─────────────────────────────────────────────────────
        m_datei = tk.Menu(menubar, **kw)
        m_datei.add_command(label="Datei auswählen",
                            command=self._choose_file, accelerator="Strg+O")
        m_datei.add_separator()
        m_datei.add_command(label="Text speichern  (TXT)",
                            command=self._save_text, accelerator="Strg+S")
        m_datei.add_command(label="Als DOCX speichern  [PRO]",
                            command=self._save_as_docx, accelerator="Strg+D")
        m_datei.add_command(label="Als PDF speichern  [PRO]",
                            command=self._save_as_pdf, accelerator="Strg+P")
        m_datei.add_separator()
        m_datei.add_command(label="Beenden", command=self.destroy, accelerator="Alt+F4")
        menubar.add_cascade(label="Datei", menu=m_datei)

        # ── Bearbeiten ────────────────────────────────────────────────
        m_bearb = tk.Menu(menubar, **kw)
        m_bearb.add_command(label="Markierten Text kopieren",
                            command=self._copy_selected_text, accelerator="Strg+C")
        m_bearb.add_command(label="Alles kopieren",
                            command=self._copy_text, accelerator="Strg+Shift+C")
        m_bearb.add_separator()
        m_bearb.add_command(label="Textbearbeitung ein/aus  [PRO]",
                            command=self._toggle_edit_mode, accelerator="Strg+E")
        m_bearb.add_separator()
        m_bearb.add_command(label="Text leeren", command=self._clear_text)
        menubar.add_cascade(label="Bearbeiten", menu=m_bearb)

        # ── PRO ───────────────────────────────────────────────────────
        m_pro = tk.Menu(menubar, **kw)
        m_pro.add_command(label="📦  Batch-Verarbeitung",
                          command=self._open_batch_dialog, accelerator="Strg+B")
        m_pro.add_separator()
        m_pro.add_command(label="Als DOCX speichern",
                          command=self._save_as_docx)
        m_pro.add_command(label="Als PDF speichern",
                          command=self._save_as_pdf)
        m_pro.add_separator()
        m_pro.add_command(label="Textbearbeitung ein/aus",
                          command=self._toggle_edit_mode)
        menubar.add_cascade(label="PRO", menu=m_pro)

        # ── Hilfe ─────────────────────────────────────────────────────
        m_hilfe = tk.Menu(menubar, **kw)
        m_hilfe.add_command(label="Hilfe öffnen",
                            command=self._show_info, accelerator="F1")
        m_hilfe.add_command(label="Lizenz anzeigen",
                            command=self._show_license_dialog)
        menubar.add_cascade(label="Hilfe", menu=m_hilfe)

        self.config(menu=menubar)

        # Tastenkürzel
        self.bind_all("<Control-o>", lambda e: self._choose_file())
        self.bind_all("<Control-O>", lambda e: self._choose_file())
        self.bind_all("<Control-s>", lambda e: self._save_text())
        self.bind_all("<Control-S>", lambda e: self._save_text())
        self.bind_all("<Control-d>", lambda e: self._save_as_docx())
        self.bind_all("<Control-D>", lambda e: self._save_as_docx())
        self.bind_all("<Control-p>", lambda e: self._save_as_pdf())
        self.bind_all("<Control-P>", lambda e: self._save_as_pdf())
        self.bind_all("<Control-b>", lambda e: self._open_batch_dialog())
        self.bind_all("<Control-B>", lambda e: self._open_batch_dialog())
        self.bind_all("<Control-e>", lambda e: self._toggle_edit_mode())
        self.bind_all("<Control-E>", lambda e: self._toggle_edit_mode())
        self.bind_all("<F1>",        lambda e: self._show_info())

    # ---- HEADER -----------------------------------------------------------

    def _build_header(self):
        self.header_frame = ctk.CTkFrame(
            self, fg_color=(LIGHT_CARD, NAVY_DARK), corner_radius=0, height=86
        )
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=0, minsize=220)
        self.header_frame.grid_columnconfigure(1, weight=1, minsize=200)
        self.header_frame.grid_columnconfigure(2, weight=0)
        self.header_frame.grid_propagate(False)

        import sys
        _base     = (sys._MEIPASS
                     if hasattr(sys, "_MEIPASS")
                     else os.path.normpath(os.path.join(os.path.dirname(__file__), "..")))
        logo_path = os.path.join(_base, LOGO_PATH)
        if os.path.isfile(logo_path):
            pil_orig = Image.open(logo_path).convert("RGBA")
            r, g, b, a = pil_orig.split()
            pil_inv = Image.merge("RGBA", (
                r.point(lambda x: 255 - x),
                g.point(lambda x: 255 - x),
                b.point(lambda x: 255 - x),
                a,
            ))
            max_w, max_h = 200, 52
            orig_w, orig_h = pil_orig.size
            scale = min(max_w / orig_w, max_h / orig_h)
            dw = int(orig_w * scale)
            dh = int(orig_h * scale)
            self._logo_img = ctk.CTkImage(
                light_image=pil_orig, dark_image=pil_inv, size=(dw, dh))
            logo_widget = ctk.CTkLabel(
                self.header_frame, image=self._logo_img, text="",
                bg_color=(LIGHT_CARD, NAVY_DARK))
        else:
            logo_widget = ctk.CTkLabel(
                self.header_frame, text=COMPANY_NAME,
                font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SECTION, weight="bold"),
                text_color=(NAVY_DARK, WHITE), bg_color=(LIGHT_CARD, NAVY_DARK))
        logo_widget.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        title_frame = ctk.CTkFrame(self.header_frame, fg_color=(LIGHT_CARD, NAVY_DARK))
        title_frame.grid(row=0, column=1, sticky="ew", padx=(0, 10), pady=12)
        title_frame.grid_columnconfigure(0, weight=1)

        # Titel zeigt PRO-Badge wenn zutreffend
        edition_badge = "  [PRO]" if self._is_pro() else ""
        ctk.CTkLabel(
            title_frame,
            text=f"{APP_NAME}{edition_badge}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_TITLE, weight="bold"),
            text_color=(NAVY_DARK, WHITE),
            bg_color=(LIGHT_CARD, NAVY_DARK),
            anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=(0, 4))

        ctk.CTkLabel(
            title_frame,
            text="Texterkennung aus PDF-, Bild-, Office- und weiteren Dateien",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_SUBTITLE),
            text_color=(TEXT_MUTED, "#6b8caa"),
            bg_color=(LIGHT_CARD, NAVY_DARK),
            anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=(0, 4))

        btn_frame = ctk.CTkFrame(self.header_frame, fg_color=(LIGHT_CARD, NAVY_DARK))
        btn_frame.grid(row=0, column=2, padx=(0, 20), pady=12, sticky="e")

        self.seg_theme = ctk.CTkSegmentedButton(
            btn_frame,
            values=[THEME_LIGHT, THEME_DARK],
            command=self._on_theme_change,
            height=32,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BODY),
            text_color=WHITE,
            text_color_disabled="#7a9ab8",
            selected_color=(NAVY_DARK, BLUE_ACCENT),
            selected_hover_color=(NAVY_MED, "#1a4fa8"),
            unselected_color=("#4a6a8a", "#1a3550"),
            unselected_hover_color=("#3a5a7a", NAVY_MED),
            fg_color=("#3a5a7a", NAVY_MED),
            corner_radius=8,
        )
        self.seg_theme.set(THEME_DARK if self._is_dark else THEME_LIGHT)
        self.seg_theme.grid(row=0, column=0, padx=(0, 8))

    # ---- CONTENT BEREICH --------------------------------------------------

    def _build_content(self):
        self.content_frame = ctk.CTkFrame(
            self, fg_color=(LIGHT_BG, DARK_BG), corner_radius=0)
        self.content_frame.grid(row=1, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)
        self.content_frame.grid_rowconfigure(1, weight=0)
        self.content_frame.grid_rowconfigure(2, weight=1)
        self.content_frame.grid_rowconfigure(3, weight=0)

        self._build_action_bar()
        self._build_drop_zone()
        self._build_textbox()
        self._build_bottom_buttons()

    def _build_action_bar(self):
        bar = ctk.CTkFrame(
            self.content_frame, fg_color=(LIGHT_BG, DARK_BG), corner_radius=0)
        bar.grid(row=0, column=0, padx=24, pady=(20, 8), sticky="ew")
        bar.grid_columnconfigure(3, weight=1)

        # Datei auswählen
        self.btn_choose = ctk.CTkButton(
            bar, text="📂  Datei auswählen",
            width=185, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BUTTON, weight="bold"),
            fg_color=BLUE_ACCENT, hover_color=NAVY_MED, corner_radius=8,
            command=self._choose_file,
        )
        self.btn_choose.grid(row=0, column=0, padx=(0, 10))

        # PRO: Batch-Button
        self.btn_batch = ctk.CTkButton(
            bar, text="📦  Batch  [PRO]",
            width=150, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BUTTON, weight="bold"),
            fg_color=NAVY_MED, hover_color=NAVY_DARK, corner_radius=8,
            command=self._open_batch_dialog,
        )
        self.btn_batch.grid(row=0, column=1, padx=(0, 10))

        # PRO: Bearbeitungs-Toggle
        self.btn_edit_toggle = ctk.CTkButton(
            bar, text="✏  Bearbeiten  [PRO]",
            width=170, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BUTTON, weight="bold"),
            fg_color=("#6b7c93", "#2a3a4a"), hover_color=NAVY_MED, corner_radius=8,
            command=self._toggle_edit_mode,
        )
        self.btn_edit_toggle.grid(row=0, column=2, padx=(0, 14))

        # Fortschrittsbalken
        self.progress = ctk.CTkProgressBar(
            bar, width=175, mode="indeterminate",
            fg_color=("#dce3ec", "#1e3a5a"), progress_color=BLUE_ACCENT)
        self.progress.grid(row=0, column=3, padx=(0, 14), sticky="w")
        self.progress.grid_remove()

        # Status
        self.lbl_status = ctk.CTkLabel(
            bar, text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BODY),
            text_color=(TEXT_MUTED, "#6b8caa"))
        self.lbl_status.grid(row=0, column=4, sticky="w")

    def _build_drop_zone(self):
        self.drop_zone = ctk.CTkFrame(
            self.content_frame,
            fg_color=(LIGHT_CARD, DARK_CARD), corner_radius=10,
            border_width=2, border_color=("#c2cede", "#3a6a9a"))
        self.drop_zone.grid(row=1, column=0, padx=24, pady=(4, 8), sticky="ew")
        self.drop_zone.grid_columnconfigure(0, weight=1)

        hint = "PDF, JPG, PNG, DOCX, XLSX, PPTX" + (
            " + TXT, ODT, RTF  [PRO]" if self._is_pro() else "")
        self.lbl_file = ctk.CTkLabel(
            self.drop_zone,
            text=f"📂  Datei hier ablegen  –  oder Schaltfläche nutzen  ({hint})",
            anchor="w",
            text_color=(TEXT_MUTED, "#6b8caa"),
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BODY),
        )
        self.lbl_file.grid(row=0, column=0, padx=16, pady=13, sticky="ew")

    def _build_textbox(self):
        self.textbox = ctk.CTkTextbox(
            self.content_frame,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BUTTON),
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
        self._setup_textbox_extras()

    def _setup_textbox_extras(self):
        dark = self._is_dark
        self._ctx_menu = tk.Menu(
            self, tearoff=0, font=(FONT_FAMILY, 11),
            bg="#132030" if dark else "#ffffff",
            fg="#e8eaf0" if dark else NAVY_DARK,
            activebackground=BLUE_ACCENT, activeforeground="#ffffff",
            relief="flat", bd=1,
        )
        self._ctx_menu.add_command(
            label="📋  Kopieren", command=self._copy_selected_text, accelerator="Strg+C")
        self._ctx_menu.add_command(
            label="☑  Alles markieren", command=self._select_all_text, accelerator="Strg+A")
        self._ctx_menu.add_separator()
        self._ctx_menu.add_command(
            label="📄  Alles kopieren", command=self._copy_text)

        _inner = getattr(self.textbox, "_textbox", None)
        for w in filter(None, [self.textbox, _inner]):
            w.bind("<Button-3>", self._show_ctx_menu)
            w.bind("<Control-a>", lambda e: (self._select_all_text(), "break")[1])
            w.bind("<Control-A>", lambda e: (self._select_all_text(), "break")[1])

    def _show_ctx_menu(self, event):
        try:
            sel = self.textbox.get("sel.first", "sel.last")
            has_sel = bool(sel.strip())
        except Exception:
            has_sel = False
        self._ctx_menu.entryconfig(0, state="normal" if has_sel else "disabled")
        try:
            self._ctx_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self._ctx_menu.grab_release()
        return "break"

    def _select_all_text(self):
        _inner = getattr(self.textbox, "_textbox", self.textbox)
        self.textbox.configure(state="normal")
        _inner.tag_add("sel", "1.0", "end-1c")
        self.textbox.configure(state="disabled" if not self._edit_mode else "normal")
        self.textbox.focus_set()

    def _copy_selected_text(self):
        try:
            text = self.textbox.get("sel.first", "sel.last")
            if text.strip():
                self.clipboard_clear()
                self.clipboard_append(text)
                self._set_status(f"Markierung kopiert  ({len(text)} Zeichen) ✓")
            else:
                messagebox.showinfo("Kein Text markiert",
                                    "Bitte zuerst Text im Editor markieren\n"
                                    "(Maus ziehen oder Strg+A für alles).")
        except Exception:
            messagebox.showinfo("Kein Text markiert",
                                "Bitte zuerst Text im Editor markieren\n"
                                "(Maus ziehen oder Strg+A für alles).")

    def _build_bottom_buttons(self):
        bar = ctk.CTkFrame(
            self.content_frame, fg_color=(LIGHT_BG, DARK_BG), corner_radius=0)
        bar.grid(row=3, column=0, padx=24, pady=(0, 16), sticky="e")

        ctk.CTkButton(
            bar, text="✂  Markierten Text kopieren",
            width=220, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BUTTON),
            fg_color=BLUE_ACCENT, hover_color=NAVY_MED, text_color=WHITE, corner_radius=8,
            command=self._copy_selected_text,
        ).grid(row=0, column=0, padx=(0, 10))

        ctk.CTkButton(
            bar, text="📋  Alles kopieren",
            width=170, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BUTTON),
            fg_color="#1a7a4a", hover_color="#145f39", text_color=WHITE, corner_radius=8,
            command=self._copy_text,
        ).grid(row=0, column=1, padx=(0, 10))

        ctk.CTkButton(
            bar, text="💾  Speichern (TXT)",
            width=160, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BUTTON),
            fg_color=NAVY_DARK, hover_color=NAVY_MED, corner_radius=8,
            command=self._save_text,
        ).grid(row=0, column=2, padx=(0, 10))

        # PRO-Export-Buttons
        self.btn_save_docx = ctk.CTkButton(
            bar, text="📝  Als DOCX  [PRO]",
            width=155, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BUTTON),
            fg_color=("#3a6a9a", "#1a3a5a"), hover_color=NAVY_MED, corner_radius=8,
            command=self._save_as_docx,
        )
        self.btn_save_docx.grid(row=0, column=3, padx=(0, 10))

        self.btn_save_pdf = ctk.CTkButton(
            bar, text="📄  Als PDF  [PRO]",
            width=145, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BUTTON),
            fg_color=("#3a6a9a", "#1a3a5a"), hover_color=NAVY_MED, corner_radius=8,
            command=self._save_as_pdf,
        )
        self.btn_save_pdf.grid(row=0, column=4, padx=(0, 10))

        ctk.CTkButton(
            bar, text="🗑  Text leeren",
            width=150, height=36,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_BUTTON),
            fg_color="#b91c1c", hover_color="#991818", text_color=WHITE, corner_radius=8,
            command=self._clear_text,
        ).grid(row=0, column=5)

    # ---- FOOTER -----------------------------------------------------------

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color=NAVY_DARK, corner_radius=0, height=38)
        footer.grid(row=2, column=0, sticky="ew")
        footer.grid_columnconfigure(0, weight=0)
        footer.grid_columnconfigure(1, weight=1)
        footer.grid_columnconfigure(2, weight=0)
        footer.grid_columnconfigure(3, weight=0)
        footer.grid_propagate(False)

        status_text  = lm.get_status_text()
        status_color = "#16a34a" if lm.is_activated() else (
                       "#e87a2a" if not lm.is_trial_expired() else "#dc2626")
        self.lbl_license = ctk.CTkLabel(
            footer,
            text=f"🔑  {status_text}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_FOOTER),
            text_color=status_color,
        )
        self.lbl_license.grid(row=0, column=0, padx=(16, 0), pady=8, sticky="w")

        ctk.CTkLabel(
            footer,
            text=f"{COMPANY_NAME}  |  {COMPANY_EMAIL}  |  {COMPANY_WEBSITE}  |  Version {APP_VERSION}",
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_FOOTER),
            text_color="#6b8caa",
        ).grid(row=0, column=2, pady=8)

        ctk.CTkButton(
            footer, text="🔑 Lizenz",
            width=80, height=24,
            font=ctk.CTkFont(family=FONT_FAMILY, size=FONT_FOOTER),
            fg_color="transparent", border_width=1, border_color="#2a4a6a",
            text_color="#6b8caa", hover_color=NAVY_MED, corner_radius=4,
            command=self._show_license_dialog,
        ).grid(row=0, column=3, padx=(8, 16), pady=8)

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
        if ext not in self._supported_exts():
            if ext in _PRO_EXTS:
                messagebox.showwarning(
                    "PRO-Feature",
                    f"'{ext}'-Dateien sind nur in der PRO-Version verfügbar.",
                    parent=self)
            else:
                messagebox.showwarning(
                    "Nicht unterstützt",
                    f"Dateityp '{ext}' wird nicht unterstützt.\n\n"
                    "Unterstützt: PDF, JPG, PNG, TIFF, DOCX, XLSX, PPTX"
                    + (" + TXT, ODT, RTF [PRO]" if not self._is_pro() else ""),
                    parent=self)
            return
        self._load_file(path)

    # ------------------------------------------------------------------ #
    #  Theme                                                              #
    # ------------------------------------------------------------------ #

    def _on_theme_change(self, value: str):
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

    # ------------------------------------------------------------------ #
    #  Lizenz                                                             #
    # ------------------------------------------------------------------ #

    def _show_info(self):
        InfoDialog(self)

    def _check_license_on_startup(self):
        from src.ui.license_dialog import LicenseDialog
        dlg = LicenseDialog(self)
        self.wait_window(dlg)
        if dlg.result is None:
            self.destroy()
            return
        self._refresh_license_status()
        self.deiconify()
        self.lift()
        self.focus_force()

    def _show_license_dialog(self):
        from src.ui.license_dialog import LicenseDialog
        dlg = LicenseDialog(self)
        self.wait_window(dlg)
        self._refresh_license_status()

    def _refresh_license_status(self):
        status_text  = lm.get_status_text()
        status_color = "#16a34a" if lm.is_activated() else (
                       "#e87a2a" if not lm.is_trial_expired() else "#dc2626")
        self.lbl_license.configure(
            text=f"🔑  {status_text}", text_color=status_color)

    # ------------------------------------------------------------------ #
    #  Datei laden & Extraktion                                           #
    # ------------------------------------------------------------------ #

    def _choose_file(self):
        std = "*.pdf *.jpg *.jpeg *.png *.tiff *.tif *.bmp *.docx *.xlsx *.pptx"
        pro = "*.txt *.odt *.rtf"
        all_exts = f"{std} {pro}" if self._is_pro() else std
        filetypes = [
            ("Alle unterstützten Dateien", all_exts),
            ("PDF-Dateien", "*.pdf"),
            ("Bilder", "*.jpg *.jpeg *.png *.tiff *.tif *.bmp"),
            ("Word-Dokumente", "*.docx"),
            ("Excel-Tabellen", "*.xlsx"),
            ("PowerPoint", "*.pptx"),
        ]
        if self._is_pro():
            filetypes += [
                ("Textdateien  [PRO]", "*.txt"),
                ("ODT-Dateien  [PRO]", "*.odt"),
                ("RTF-Dateien  [PRO]", "*.rtf"),
            ]
        filetypes.append(("Alle Dateien", "*.*"))
        path = filedialog.askopenfilename(title="Datei auswählen", filetypes=filetypes)
        if path:
            self._load_file(path)

    def _load_file(self, path: str):
        self._selected_file = path
        filename = os.path.basename(path)
        self.lbl_file.configure(text=f"📄  {filename}", text_color=(NAVY_DARK, WHITE))
        self._set_status("")
        self.after(100, self._start_extraction)

    def _start_extraction(self):
        if not self._selected_file:
            return
        self.btn_choose.configure(state="disabled")
        self.progress.grid()
        self.progress.start()
        self._set_status("Verarbeite …")
        threading.Thread(target=self._run_extraction, daemon=True).start()

    def _run_extraction(self):
        try:
            result = route_file(self._selected_file, allow_pro=self._is_pro())
        except Exception as e:
            result = f"Unerwarteter Fehler: {e}"
        self.after(0, self._show_result, result)

    def _show_result(self, text: str):
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", text)
        if not self._edit_mode:
            self.textbox.configure(state="disabled")
        self.progress.stop()
        self.progress.grid_remove()
        self.btn_choose.configure(state="normal")
        self._set_status("Fertig ✓")

    # ------------------------------------------------------------------ #
    #  PRO: Textbearbeitung                                               #
    # ------------------------------------------------------------------ #

    def _toggle_edit_mode(self):
        if not self._pro_guard("Textbearbeitung"):
            return
        self._edit_mode = not self._edit_mode
        if self._edit_mode:
            self.textbox.configure(state="normal",
                                   border_color=(SUCCESS, SUCCESS))
            self.btn_edit_toggle.configure(
                text="✏  Bearbeitung aktiv",
                fg_color=(SUCCESS, "#14803e"),
            )
            self._set_status("Textbearbeitung aktiv – Text kann direkt bearbeitet werden.")
        else:
            self.textbox.configure(state="disabled",
                                   border_color=("#c2cede", "#3a6a9a"))
            self.btn_edit_toggle.configure(
                text="✏  Bearbeiten  [PRO]",
                fg_color=("#6b7c93", "#2a3a4a"),
            )
            self._set_status("Textbearbeitung deaktiviert.")

    # ------------------------------------------------------------------ #
    #  PRO: Batch-Verarbeitung                                            #
    # ------------------------------------------------------------------ #

    def _open_batch_dialog(self):
        if not self._pro_guard("Batch-Verarbeitung"):
            return
        from src.ui.batch_dialog import BatchDialog
        dlg = BatchDialog(self, allow_pro=True)
        self.wait_window(dlg)
        if dlg.result:
            self._show_result(dlg.result)
            self._selected_file = ""
            self.lbl_file.configure(
                text="📦  Batch-Ergebnis (mehrere Dateien)",
                text_color=(NAVY_DARK, WHITE))
            self._set_status(f"Batch abgeschlossen ✓")

    # ------------------------------------------------------------------ #
    #  Kopieren, Speichern & Leeren                                       #
    # ------------------------------------------------------------------ #

    def _clear_text(self):
        self.textbox.configure(state="normal")
        self.textbox.delete("0.0", "end")
        self.textbox.insert("0.0", "Hier erscheint der erkannte Text …")
        self.textbox.configure(state="disabled" if not self._edit_mode else "normal")
        self._edit_mode = False
        self.btn_edit_toggle.configure(
            text="✏  Bearbeiten  [PRO]", fg_color=("#6b7c93", "#2a3a4a"))
        self._selected_file = ""
        hint = "PDF, JPG, PNG, DOCX, XLSX, PPTX" + (
            " + TXT, ODT, RTF  [PRO]" if self._is_pro() else "")
        self.lbl_file.configure(
            text=f"📂  Datei hier ablegen  –  oder Schaltfläche nutzen  ({hint})",
            text_color=(TEXT_MUTED, "#6b8caa"))
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

    def _save_as_docx(self):
        if not self._pro_guard("DOCX-Export"):
            return
        text = self.textbox.get("0.0", "end").strip()
        if not text:
            messagebox.showinfo("Info", "Kein Text zum Speichern vorhanden.")
            return
        default_name = "export.docx"
        if self._selected_file:
            base = os.path.splitext(os.path.basename(self._selected_file))[0]
            default_name = f"{base}_export.docx"
        save_path = filedialog.asksaveasfilename(
            title="Als DOCX speichern", defaultextension=".docx",
            initialfile=default_name,
            filetypes=[("Word-Dokument", "*.docx"), ("Alle Dateien", "*.*")],
        )
        if not save_path:
            return
        from src.pro_exporter import export_docx
        ok, msg = export_docx(text, save_path)
        if ok:
            self._set_status(f"DOCX gespeichert: {os.path.basename(save_path)} ✓")
        else:
            messagebox.showerror("DOCX-Export fehlgeschlagen", msg, parent=self)

    def _save_as_pdf(self):
        if not self._pro_guard("PDF-Export"):
            return
        text = self.textbox.get("0.0", "end").strip()
        if not text:
            messagebox.showinfo("Info", "Kein Text zum Speichern vorhanden.")
            return
        default_name = "export.pdf"
        if self._selected_file:
            base = os.path.splitext(os.path.basename(self._selected_file))[0]
            default_name = f"{base}_export.pdf"
        save_path = filedialog.asksaveasfilename(
            title="Als PDF speichern", defaultextension=".pdf",
            initialfile=default_name,
            filetypes=[("PDF-Datei", "*.pdf"), ("Alle Dateien", "*.*")],
        )
        if not save_path:
            return
        from src.pro_exporter import export_pdf
        ok, msg = export_pdf(text, save_path)
        if ok:
            self._set_status(f"PDF gespeichert: {os.path.basename(save_path)} ✓")
        else:
            messagebox.showerror("PDF-Export fehlgeschlagen", msg, parent=self)

    def _set_status(self, message: str):
        self.lbl_status.configure(text=message)
