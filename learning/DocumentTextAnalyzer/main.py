"""
main.py - Einstiegspunkt fuer DocumentTextAnalyzer
Starte die Anwendung mit:  python main.py
"""

import sys
import os
import ctypes

# ── DPI-Awareness ZUERST setzen (vor jedem tkinter-Import!) ──────────
# Ohne das rendert Windows tkinter/customtkinter unscharf auf HiDPI-Displays.
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)   # Per-Monitor DPI aware v1
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()    # Fallback: System DPI aware
    except Exception:
        pass

# Sicherstellen, dass das Projektverzeichnis im Suchpfad liegt
sys.path.insert(0, os.path.dirname(__file__))

from src.app import DocumentTextAnalyzerApp


def main():
    app = DocumentTextAnalyzerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
