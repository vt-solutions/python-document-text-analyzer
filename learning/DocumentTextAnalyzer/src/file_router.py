"""
file_router.py
Erkennt den Dateityp anhand der Endung und ruft den passenden Extractor auf.
"""

import os
from src.pdf_extractor import extract_pdf
from src.image_ocr import extract_image_ocr
from src.office_extractor import extract_docx, extract_xlsx, extract_pptx


# STANDARD-Formate (alle Editionen)
_STANDARD_EXTS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp",
    ".docx", ".xlsx", ".pptx",
}

# Zusätzliche PRO-Formate
_PRO_EXTS = {".txt", ".odt", ".rtf"}

ALL_SUPPORTED_EXTS = _STANDARD_EXTS | _PRO_EXTS


def route_file(file_path: str, allow_pro: bool = False) -> str:
    """
    Leitet die Datei an den passenden Extractor weiter.

    allow_pro: True wenn die aktuelle Edition PRO-Features erlaubt.
    """
    if not os.path.isfile(file_path):
        return f"Fehler: Datei nicht gefunden: {file_path}"

    ext = os.path.splitext(file_path)[1].lower()

    # ── STANDARD-Formate ──────────────────────────────────────────────
    if ext == ".pdf":
        return extract_pdf(file_path)
    if ext in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"):
        return extract_image_ocr(file_path)
    if ext == ".docx":
        return extract_docx(file_path)
    if ext == ".xlsx":
        return extract_xlsx(file_path)
    if ext == ".pptx":
        return extract_pptx(file_path)

    # ── PRO-Formate ───────────────────────────────────────────────────
    if ext in _PRO_EXTS:
        if not allow_pro:
            return (
                f"'{ext}'-Dateien sind nur in der PRO-Version verfügbar.\n\n"
                "Upgraden Sie auf VT Document Text Converter PRO,\n"
                "um .txt, .odt und .rtf-Dateien zu verarbeiten."
            )
        from src.pro_extractor import extract_txt, extract_odt, extract_rtf
        if ext == ".txt":
            return extract_txt(file_path)
        if ext == ".odt":
            return extract_odt(file_path)
        if ext == ".rtf":
            return extract_rtf(file_path)

    return f"Nicht unterstützter Dateityp: {ext}"
