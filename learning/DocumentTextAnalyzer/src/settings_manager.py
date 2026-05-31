"""
settings_manager.py
Laedt und speichert Benutzereinstellungen (Theme, etc.)
Speicherort: %APPDATA%\vt-solutions\VTConverter\settings.json
"""

import json
import os
from pathlib import Path

_SETTINGS_DIR  = Path(os.environ.get("APPDATA", Path.home())) / "vt-solutions" / "VTConverter"
_SETTINGS_FILE = _SETTINGS_DIR / "settings.json"

_DEFAULTS: dict = {
    "theme": "Dark",
}


def load() -> dict:
    """Gibt gespeicherte Einstellungen zurück, fehlende Keys mit Default auffüllen."""
    try:
        if _SETTINGS_FILE.exists():
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            return {**_DEFAULTS, **data}
    except Exception:
        pass
    return _DEFAULTS.copy()


def save(data: dict) -> None:
    """Speichert übergebene Einstellungen (merge mit vorhandenen)."""
    try:
        _SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        existing = load()
        existing.update(data)
        with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)
    except Exception:
        pass
