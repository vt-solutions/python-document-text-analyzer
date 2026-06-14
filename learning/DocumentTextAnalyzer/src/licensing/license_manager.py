"""
license_manager.py
Lizenzsystem für VT Document Text Converter.

Editionen:
  TRIAL    – 30-Tage-Testversion, gleiche Funktionen wie STANDARD
  STANDARD – Grundfunktionen (PDF, Bild-OCR, Office-Formate, Kopieren/Speichern als TXT)
  PRO      – Alle Funktionen: neue Formate (.txt/.odt/.rtf), DOCX/PDF-Export,
             Batch-Verarbeitung, Textbearbeitung im Editor

Schlüsselformat:  VT-YYYY-EPPP-CCCC
  YYYY = Jahr, E = Editions-Code (S/P), PPP = Seriennummer (Base36), CCCC = HMAC-Signatur

Validierung: HMAC-SHA256 (offline, ohne Internetverbindung). Zufällige oder manipulierte
Schlüssel werden mit Sicherheit abgelehnt. Neue Schlüssel werden mit tools/keygen.py erzeugt.

Datei: %APPDATA%\\vt-solutions\\VTConverter\\license.json
"""

import json
import os
import re
from datetime import datetime, timedelta
from pathlib import Path

from src.licensing.license_crypto import validate_key as _crypto_validate, get_machine_id

# ── Pfade ─────────────────────────────────────────────────────────────── #
_DIR  = Path(os.environ.get("APPDATA", Path.home())) / "vt-solutions" / "VTConverter"
_FILE = _DIR / "license.json"

# ── Formate & Konstanten ──────────────────────────────────────────────── #
KEY_PATTERN = re.compile(r"^VT-\d{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$", re.IGNORECASE)

TRIAL_DAYS = 30

# Auf True setzen, um Lizenz an den Aktivierungs-PC zu binden.
# Achtung: Bei Hardware-Wechsel muss der Nutzer erneut aktivieren.
MACHINE_BINDING_ENABLED = False

# ── Feature-Gates ─────────────────────────────────────────────────────── #
_FEATURES: dict[str, set[str]] = {
    "TRIAL":    {"basic_extraction", "copy", "save_txt"},
    "STANDARD": {"basic_extraction", "copy", "save_txt"},
    "PRO": {
        "basic_extraction", "copy", "save_txt",
        "extra_formats",   # .txt, .odt, .rtf
        "export_docx",     # Als DOCX speichern
        "export_pdf",      # Als PDF speichern
        "batch",           # Batch-Verarbeitung
        "edit_text",       # Textbearbeitung im Editor
    },
}


def has_feature(feature: str) -> bool:
    """Gibt True zurück, wenn die aktive Edition das Feature enthält."""
    edition = get_edition()
    return feature in _FEATURES.get(edition, set())


# ── Datei-I/O ─────────────────────────────────────────────────────────── #

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


# ── Validierung ───────────────────────────────────────────────────────── #

def validate_format(key: str) -> bool:
    """Schnell-Prüfung: Stimmt das Schlüsselformat?"""
    return bool(KEY_PATTERN.match(key.strip()))


def validate_key(key: str) -> tuple[bool, str]:
    """
    Prüft Schlüssel vollständig (Format + kryptografische Signatur).
    Rückgabe: (gültig, edition) – edition ist '' bei ungültigem Schlüssel.
    """
    key = key.strip().upper()
    if not validate_format(key):
        return False, ""
    return _crypto_validate(key)


# ── Hardware-Bindung ──────────────────────────────────────────────────── #

def check_machine_binding() -> bool:
    """
    Gibt True zurück, wenn die Hardware-Bindung deaktiviert ist oder
    der aktuelle PC mit dem Aktivierungs-PC übereinstimmt.
    """
    if not MACHINE_BINDING_ENABLED:
        return True
    data = load()
    stored_id = data.get("machine_id")
    if not stored_id:
        return True
    return stored_id == get_machine_id()


# ── Aktionen ──────────────────────────────────────────────────────────── #

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
            "Beispiel: VT-2026-P001-XXXX\n\n"
            "Bitte prüfen Sie die Schreibweise oder wenden Sie sich\n"
            "an support@vt-solutions.de."
        )

    data: dict = {
        "customer":     customer,
        "license_key":  key,
        "activated":    True,
        "edition":      edition,
        "activated_at": datetime.now().isoformat(),
    }

    if MACHINE_BINDING_ENABLED:
        data["machine_id"] = get_machine_id()

    _save(data)

    label = {"PRO": "PRO", "STANDARD": "Standard"}.get(edition, edition)
    return True, f"Lizenz erfolgreich aktiviert!\nEdition: {label}\nKunde: {customer}"


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


# ── Status-Abfragen ───────────────────────────────────────────────────── #

def is_first_run() -> bool:
    return not _FILE.exists()


def is_activated() -> bool:
    if not load().get("activated", False):
        return False
    return check_machine_binding()


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
        if MACHINE_BINDING_ENABLED and not check_machine_binding():
            return "Lizenz – Anderer PC"
        label = {"PRO": "PRO", "STANDARD": "Standard"}.get(
            data.get("edition", ""), data.get("edition", "")
        )
        return f"{label}  ·  {data.get('customer', '')}"

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
