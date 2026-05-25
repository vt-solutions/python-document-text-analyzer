"""
file_router.py
Erkennt den Dateityp anhand der Endung und ruft den passenden Extractor auf.
"""

import os
from src.pdf_extractor import extract_pdf
from src.image_ocr import extract_image_ocr
from src.office_extractor import extract_docx, extract_xlsx, extract_pptx


def route_file(file_path: str) -> str:
    """
    Leitet die Datei an den passenden Extractor weiter.
    Gibt den erkannten Text als String zurück.
    """
    if not os.path.isfile(file_path):
        return f"Fehler: Datei nicht gefunden: {file_path}"

    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_pdf(file_path)
    elif ext in (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"):
        return extract_image_ocr(file_path)
    elif ext == ".docx":
        return extract_docx(file_path)
    elif ext == ".xlsx":
        return extract_xlsx(file_path)
    elif ext == ".pptx":
        return extract_pptx(file_path)
    else:
        return f"Nicht unterstützter Dateityp: {ext}"
