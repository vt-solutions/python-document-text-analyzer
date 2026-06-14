"""
pro_extractor.py
PRO-Extraktoren fuer zusaetzliche Dateiformate: .txt, .odt, .rtf
"""

import os


def extract_txt(file_path: str) -> str:
    """Liest eine Plain-Text-Datei (UTF-8 mit BOM-Fallback)."""
    for enc in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            with open(file_path, "r", encoding=enc) as f:
                return f.read()
        except (UnicodeDecodeError, LookupError):
            continue
    return "Fehler: Textdatei konnte nicht gelesen werden."


def extract_odt(file_path: str) -> str:
    """Extrahiert Text aus einer ODT-Datei (LibreOffice Writer)."""
    try:
        from odf.opendocument import load as odf_load
        from odf.text import P
        from odf.element import Text

        doc = odf_load(file_path)
        paragraphs = []
        for p in doc.getElementsByType(P):
            parts = []
            _collect_text(p, parts)
            paragraphs.append("".join(parts))
        return "\n".join(paragraphs).strip() or "(Kein Text gefunden)"
    except ImportError:
        return (
            "ODT-Unterstützung nicht verfügbar.\n"
            "Bitte installieren Sie: pip install odfpy"
        )
    except Exception as e:
        return f"Fehler beim Lesen der ODT-Datei: {e}"


def _collect_text(element, parts: list) -> None:
    """Rekursiv Text aus einem ODF-Element extrahieren."""
    from odf.element import Text as OdfText
    if element.nodeType == element.TEXT_NODE:
        parts.append(element.data)
    for child in element.childNodes:
        _collect_text(child, parts)


def extract_rtf(file_path: str) -> str:
    """Extrahiert Klartext aus einer RTF-Datei."""
    try:
        from striprtf.striprtf import rtf_to_text
        for enc in ("utf-8", "cp1252", "latin-1"):
            try:
                with open(file_path, "r", encoding=enc) as f:
                    raw = f.read()
                text = rtf_to_text(raw)
                return text.strip() or "(Kein Text gefunden)"
            except (UnicodeDecodeError, LookupError):
                continue
        return "Fehler: RTF-Datei konnte nicht gelesen werden."
    except ImportError:
        return (
            "RTF-Unterstützung nicht verfügbar.\n"
            "Bitte installieren Sie: pip install striprtf"
        )
    except Exception as e:
        return f"Fehler beim Lesen der RTF-Datei: {e}"
