"""
main.py - Einstiegspunkt fuer VT Document Text Converter
Starte die Anwendung mit:  python main.py
"""

import sys
import os
import ctypes
import traceback
import datetime

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

# ── Crash-Logging ─────────────────────────────────────────────────────
_LOG_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local",
                        "VT Solutions", "VT_Converter", "logs")
os.makedirs(_LOG_DIR, exist_ok=True)
_LOG_FILE = os.path.join(_LOG_DIR, "crash.log")


def _excepthook(exc_type, exc_value, exc_tb):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*60}\n{timestamp}\n")
        traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    sys.__excepthook__(exc_type, exc_value, exc_tb)


sys.excepthook = _excepthook

from src.app import DocumentTextAnalyzerApp


def main():
    app = DocumentTextAnalyzerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
