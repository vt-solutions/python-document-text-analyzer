"""
clipboard.py
Hilfsfunktionen für die Zwischenablage.
Nutzt tkinter für plattformunabhängigen Zugriff.
"""

import tkinter as tk


def copy_to_clipboard(text: str) -> bool:
    """
    Kopiert den angegebenen Text in die Windows-Zwischenablage.

    Returns:
        True bei Erfolg, False bei Fehler
    """
    try:
        root = tk.Tk()
        root.withdraw()  # Fenster verstecken
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        return True
    except Exception:
        return False
