"""
license_manager.py
Einfaches Lizenzsystem fuer VT Document Text Converter.

Schluessel-Format:  VT-YYYY-XXXX-XXXX
Beispiel:           VT-2025-ABCD-1234

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

# Interne Demo-/Test-Schlüssel (für Entwicklung und Demos)
_DEMO_KEYS: set[str] = {
    "VT-2025-DEMO-0001",
    "VT-2025-ABCD-1234",
    "VT-2026-PRO1-0001",
    "VT-2026-BETA-TEST",
}

TRIAL_DAYS = 30


# ------------------------------------------------------------------ #
#  Datei I/O                                                          #
# ------------------------------------------------------------------ #

def load() -> dict:
    """Lädt die gespeicherte Lizenzdatei. Gibt {} zurück wenn nicht vorhanden."""
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

def _checksum(key: str) -> str:
    """Interne Prüfsumme – verhindert triviale Fälschungen."""
    secret = "vt-solutions-2025"
    return hashlib.sha256(f"{secret}:{key.upper()}".encode()).hexdigest()[:8].upper()


def validate_format(key: str) -> bool:
    """Prüft nur das Format (VT-YYYY-XXXX-XXXX)."""
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
        return True, "PRO"
    # Für alle korrekt formatierten Schlüssel → STANDARD (Demo-Modus)
    # In Produktion: hier Server-API aufrufen
    return True, "STANDARD"


# ------------------------------------------------------------------ #
#  Aktionen                                                           #
# ------------------------------------------------------------------ #

def activate(customer: str, key: str) -> tuple[bool, str]:
    """
    Aktiviert die Lizenz.
    Gibt (erfolg, nachricht) zurück.
    """
    customer = customer.strip()
    key      = key.strip().upper()

    if not customer:
        return False, "Bitte Benutzernamen eingeben."

    ok, edition = validate_key(key)
    if not ok:
        return False, (
            "Ungültiger Lizenzschlüssel.\n"
            "Erwartet: VT-YYYY-XXXX-XXXX\n"
            "Beispiel: VT-2025-ABCD-1234"
        )

    data = {
        "customer":      customer,
        "license_key":   key,
        "activated":     True,
        "edition":       edition,
        "activated_at":  datetime.now().isoformat(),
    }
    _save(data)
    return True, f"Lizenz erfolgreich aktiviert!\nEdition: {edition}\nKunde: {customer}"


def start_trial() -> dict:
    """Startet eine 30-Tage-Testversion."""
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
    """Entfernt die Lizenzdatei (für Tests / Deinstallation)."""
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


def get_status_text() -> str:
    data = load()
    if not data:
        return "Nicht aktiviert"
    if data.get("activated"):
        return f"{data.get('edition', 'PRO')}  ·  {data.get('customer', '')}"
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
