"""
license_manager.py
Lizenzsystem fuer VT Document Text Converter.

Editionen:
  TRIAL    – 30-Tage-Testversion, gleiche Funktionen wie STANDARD
  STANDARD – Grundfunktionen (PDF, Bild-OCR, Office-Formate, Kopieren/Speichern als TXT)
  PRO      – Alle Funktionen: neue Formate (.txt/.odt/.rtf), DOCX/PDF-Export,
             Batch-Verarbeitung, Textbearbeitung im Editor

Schluessel-Format:  VT-YYYY-XXXX-XXXX
Beispiel:           VT-2026-PRO1-0001

Datei: %APPDATA%\\vt-solutions\\VTConverter\\license.json
"""

import json
import re
import hashlib
import os
from pathlib import Path
from datetime import datetime, timedelta

# ------------------------------------------------------------------ #
#  Konstanten                                                         #
# ------------------------------------------------------------------ #
_DIR  = Path(os.environ.get("APPDATA", Path.home())) / "vt-solutions" / "VTConverter"
_FILE = _DIR / "license.json"

KEY_PATTERN = re.compile(r"^VT-\d{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$", re.IGNORECASE)

# Demo-/Test-Schlüssel mit zugewiesener Edition
_DEMO_KEYS: dict[str, str] = {
    "VT-2025-DEMO-0001": "STANDARD",
    "VT-2025-ABCD-1234": "STANDARD",
    "VT-2026-PRO1-0001": "PRO",
    "VT-2026-PRO2-0002": "PRO",
    "VT-2026-BETA-TEST": "PRO",
}

TRIAL_DAYS = 30

# ------------------------------------------------------------------ #
#  Feature-Gates                                                      #
# ------------------------------------------------------------------ #

# Welche Editionen haben Zugriff auf welche Funktionen
_FEATURES: dict[str, set[str]] = {
    "TRIAL":    {"basic_extraction", "copy", "save_txt"},
    "STANDARD": {"basic_extraction", "copy", "save_txt"},
    "PRO": {
        "basic_extraction", "copy", "save_txt",
        "extra_formats",    # .txt, .odt, .rtf
        "export_docx",      # Als DOCX speichern
        "export_pdf",       # Als PDF speichern
        "batch",            # Batch-Verarbeitung
        "edit_text",        # Textbearbeitung im Editor
    },
}


def has_feature(feature: str) -> bool:
    """Gibt True zurück wenn die aktuelle Edition das Feature enthält."""
    edition = get_edition()
    return feature in _FEATURES.get(edition, set())


# ------------------------------------------------------------------ #
#  Datei I/O                                                          #
# ------------------------------------------------------------------ #

def load() -> dict:
    try:
        if _FILE.exists():
            with open(_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save(data: dict) -> None:
    try:
        _DIR.mkdir(parents=True, exist_ok=True)
        with open(_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ------------------------------------------------------------------ #
#  Validierung                                                        #
# ------------------------------------------------------------------ #

def validate_format(key: str) -> bool:
    return bool(KEY_PATTERN.match(key.strip()))


def validate_key(key: str) -> tuple[bool, str]:
    """
    Prüft Schlüssel vollständig.
    Gibt (gültig, edition) zurück.
    """
    key = key.strip().upper()
    if not validate_format(key):
        return False, ""
    if key in _DEMO_KEYS:
        return True, _DEMO_KEYS[key]
    # Produktion: hier Server-API aufrufen.
    # Fallback: korrekt formatierte Schlüssel → STANDARD
    return True, "STANDARD"


# ------------------------------------------------------------------ #
#  Aktionen                                                           #
# ------------------------------------------------------------------ #

def activate(customer: str, key: str) -> tuple[bool, str]:
    customer = customer.strip()
    key      = key.strip().upper()

    if not customer:
        return False, "Bitte Benutzernamen eingeben."

    ok, edition = validate_key(key)
    if not ok:
        return False, (
            "Ungültiger Lizenzschlüssel.\n"
            "Erwartet: VT-YYYY-XXXX-XXXX\n"
            "Beispiel: VT-2026-PRO1-0001"
        )

    data = {
        "customer":      customer,
        "license_key":   key,
        "activated":     True,
        "edition":       edition,
        "activated_at":  datetime.now().isoformat(),
    }
    _save(data)

    edition_label = {"PRO": "PRO", "STANDARD": "Standard"}.get(edition, edition)
    return True, f"Lizenz erfolgreich aktiviert!\nEdition: {edition_label}\nKunde: {customer}"


def start_trial() -> dict:
    data = {
        "customer":      "Testbenutzer",
        "license_key":   "TRIAL",
        "activated":     False,
        "edition":       "TRIAL",
        "trial_started": datetime.now().isoformat(),
        "trial_ends":    (datetime.now() + timedelta(days=TRIAL_DAYS)).isoformat(),
    }
    _save(data)
    return data


def deactivate() -> None:
    try:
        if _FILE.exists():
            _FILE.unlink()
    except Exception:
        pass


# ------------------------------------------------------------------ #
#  Status-Abfragen                                                    #
# ------------------------------------------------------------------ #

def is_first_run() -> bool:
    return not _FILE.exists()


def is_activated() -> bool:
    return load().get("activated", False)


def get_edition() -> str:
    return load().get("edition", "TRIAL")


def get_customer() -> str:
    return load().get("customer", "–")


def is_pro() -> bool:
    return get_edition() == "PRO"


def get_status_text() -> str:
    data = load()
    if not data:
        return "Nicht aktiviert"
    if data.get("activated"):
        edition_label = {"PRO": "PRO", "STANDARD": "Standard"}.get(
            data.get("edition", ""), data.get("edition", "")
        )
        return f"{edition_label}  ·  {data.get('customer', '')}"
    # Trial
    ends = data.get("trial_ends", "")
    if ends:
        try:
            remaining = (datetime.fromisoformat(ends) - datetime.now()).days
            if remaining < 0:
                return "Testversion abgelaufen"
            return f"Testversion  ·  noch {remaining} Tage"
        except Exception:
            pass
    return "Testversion"


def is_trial_expired() -> bool:
    data = load()
    if data.get("activated"):
        return False
    ends = data.get("trial_ends", "")
    if ends:
        try:
            return datetime.now() > datetime.fromisoformat(ends)
        except Exception:
            pass
    return False
