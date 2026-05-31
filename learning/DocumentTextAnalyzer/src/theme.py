"""
theme.py  –  Zentrale UI-Konstanten für VT Document Text Converter.
Alle Schriftgrößen, Farben und Abstände an EINEM Ort definiert.
Beide Dateien (app.py UND license_dialog.py) importieren ausschließlich hieraus.
"""

# ── Schriftart ────────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"

# ── Schriftgrößen (identisch in Hauptfenster UND Lizenz-Dialog) ───────
FONT_TITLE       = 18   # Haupttitel  „VT Document Text Converter"
FONT_SECTION     = 14   # Bereichstitel  „Lizenz aktivieren"
FONT_LABEL       = 12   # Feld-Labels  „Firmenname", „Lizenzschlüssel"
FONT_BODY        = 12   # Beschreibungstexte, normale Labels
FONT_INPUT       = 13   # Text in Eingabefeldern
FONT_BUTTON      = 13   # Button-Beschriftungen
FONT_SUBTITLE    = 11   # Untertitel unter Haupttitel
FONT_HINT        = 10   # Hinweise, Format-Texte
FONT_FOOTER      = 10   # Footer-Text
FONT_STATUS      = 12   # Status-/Fehlermeldungen

# ── Widget-Höhen ──────────────────────────────────────────────────────
HEIGHT_BUTTON    = 36   # Standard-Buttons
HEIGHT_ENTRY     = 36   # Eingabefelder

# ── Farben ────────────────────────────────────────────────────────────
NAVY_DARK        = "#0d1f35"
NAVY_MED         = "#102a47"
BLUE_ACCENT      = "#1e5fd4"
BLUE_HOVER       = "#1a4fa8"
WHITE            = "#ffffff"
LIGHT_BG         = "#f4f6f9"
LIGHT_CARD       = "#ffffff"
DARK_BG          = "#0d1520"
DARK_CARD        = "#132030"
TEXT_MUTED       = "#6b7c93"
SEP_LIGHT        = "#dce3ec"
SEP_DARK         = "#1e3a5a"
SUCCESS          = "#16a34a"
ERROR_RED        = "#dc2626"
