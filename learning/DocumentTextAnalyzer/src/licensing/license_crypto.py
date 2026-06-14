"""
license_crypto.py
HMAC-SHA256-basierte Offline-Schlüsselvalidierung für VT Document Text Converter.

Schlüsselformat:  VT-YYYY-EPPP-CCCC
  YYYY = 4-stelliges Jahr
  E    = Editions-Code ('S' = Standard, 'P' = Pro)
  PPP  = 3-stellige Seriennummer (Base36, 0–46 655)
  CCCC = 4-stellige HMAC-SHA256-Signatur (Base36)

Sicherheit: Keine Netzwerkverbindung erforderlich. Der Geheimschlüssel ist
XOR-maskiert im Code gespeichert. Zufällig generierte Schlüssel werden
mit Wahrscheinlichkeit 1 - 1/36^4 ≈ 99,99994 % abgelehnt.
"""

import hashlib
import hmac
import platform
import re
import subprocess

# ── Geheimschlüssel (XOR-maskiert, Maske = 0x4F) ─────────────────────── #
# Dekodiert: b"vt-solutions.2026.kX9#mP3r"
_MK = 0x4F
_MS = bytes([
    0x39, 0x3B, 0x62, 0x3C, 0x20, 0x23, 0x3A, 0x3B,
    0x26, 0x20, 0x21, 0x3C, 0x61, 0x7D, 0x7F, 0x7D,
    0x79, 0x61, 0x24, 0x17, 0x76, 0x6C, 0x22, 0x1F,
    0x7C, 0x3D,
])
_SECRET: bytes = bytes(b ^ _MK for b in _MS)

# ── Alphabet & Konstanten ─────────────────────────────────────────────── #
_ALPHA = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_BASE  = 36
_SIG_W = 4                   # Breite der Signatur in Zeichen
_SER_W = 3                   # Breite der Seriennummer in Zeichen
_SIG_MOD = _BASE ** _SIG_W   # 1 679 616 mögliche Signaturen

EDITION_MAP: dict[str, str] = {
    "S": "STANDARD",
    "P": "PRO",
}

# ── Base36-Codierung ──────────────────────────────────────────────────── #

def _b36enc(n: int, width: int) -> str:
    buf = []
    for _ in range(width):
        buf.append(_ALPHA[n % _BASE])
        n //= _BASE
    return "".join(reversed(buf))

# ── Signaturberechnung ────────────────────────────────────────────────── #

def _compute_sig(payload: str, year: str) -> str:
    """Berechnet die 4-stellige Base36-HMAC-Signatur für einen Payload."""
    msg = f"VT-{year}-{payload}".encode("ascii")
    digest = hmac.new(_SECRET, msg, hashlib.sha256).digest()
    val = int.from_bytes(digest[:4], "big") % _SIG_MOD
    return _b36enc(val, _SIG_W)

# ── Öffentliche API ───────────────────────────────────────────────────── #

def validate_key(key: str) -> tuple[bool, str]:
    """
    Prüft einen Lizenzschlüssel kryptografisch.

    Rückgabe: (gültig, edition)
      gültig  – True wenn Signatur stimmt
      edition – 'STANDARD' | 'PRO' | '' (leer bei ungültigem Schlüssel)
    """
    key = key.strip().upper()
    parts = key.split("-")

    if len(parts) != 4 or parts[0] != "VT":
        return False, ""

    _, year, payload, sig = parts

    if not re.fullmatch(r"\d{4}", year):
        return False, ""
    if not re.fullmatch(r"[A-Z0-9]{4}", payload):
        return False, ""
    if not re.fullmatch(r"[A-Z0-9]{4}", sig):
        return False, ""

    edition_char = payload[0]
    if edition_char not in EDITION_MAP:
        return False, ""

    expected = _compute_sig(payload, year)
    if not hmac.compare_digest(sig, expected):
        return False, ""

    return True, EDITION_MAP[edition_char]


def generate_key(edition: str, year: int, serial: int) -> str:
    """
    Erzeugt einen kryptografisch gültigen Lizenzschlüssel.

    edition: 'STANDARD' | 'PRO'
    year:    z. B. 2026
    serial:  Seriennummer 0 – 46 655 (3 Base36-Stellen)

    Nur für die interne Verwendung im Keygen-Tool.
    """
    rev = {v: k for k, v in EDITION_MAP.items()}
    if edition not in rev:
        raise ValueError(f"Unbekannte Edition: {edition!r}")

    ed_char  = rev[edition]
    ser_str  = _b36enc(serial % (_BASE ** _SER_W), _SER_W)
    payload  = f"{ed_char}{ser_str}"
    year_str = str(year).zfill(4)
    sig      = _compute_sig(payload, year_str)

    return f"VT-{year_str}-{payload}-{sig}"


# ── Geräte-ID (für optionale Hardware-Bindung) ────────────────────────── #

def get_machine_id() -> str:
    """
    Berechnet eine stabile Gerätekennung aus Systemmerkmalen.

    Verwendet: Motherboard-Seriennummer (Windows WMIC) + Hostname.
    Rückgabe: 16-stelliger Hex-Hash (SHA-256), Großbuchstaben.
    """
    parts: list[str] = []

    # Windows: Motherboard-Seriennummer
    try:
        result = subprocess.run(
            ["wmic", "baseboard", "get", "serialnumber"],
            capture_output=True, text=True, timeout=5,
        )
        lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
        if len(lines) >= 2:
            sn = lines[-1]
            _ignore = {"serialnumber", "to be filled by o.e.m.", "default string", "n/a", ""}
            if sn.lower() not in _ignore:
                parts.append(f"mb:{sn}")
    except Exception:
        pass

    # Hostname als stabiler Fallback
    parts.append(f"hn:{platform.node()}")

    combined = "|".join(parts) or "unknown-machine"
    return hashlib.sha256(combined.encode()).hexdigest()[:16].upper()
