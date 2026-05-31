"""
main.py - Einstiegspunkt fuer VT Document Text Converter
Starte die Anwendung mit:  python main.py
"""

import sys
import os
import ctypes

# ── DPI-Awareness ZUERST setzen (vor jedem tkinter-Import!) ──────────
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ── AppUserModelID setzen ─────────────────────────────────────────────
try:
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(
        "vt-solutions.VT-Document-Text-Converter.1.0"
    )
except Exception:
    pass

sys.path.insert(0, os.path.dirname(__file__))

from src.app import DocumentTextAnalyzerApp


def main():
    app = DocumentTextAnalyzerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
