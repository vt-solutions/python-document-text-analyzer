"""
pdf_extractor.py
Extrahiert Text aus PDF-Dateien.
- Normales PDF: direkte Textextraktion mit pypdf
- Gescanntes PDF: OCR mit pytesseract (Seite als Bild rendern)
"""

import io

import pytesseract
from PIL import Image
from pypdf import PdfReader

import src.ocr_config  # setzt pytesseract.tesseract_cmd  # noqa: F401


def extract_pdf(file_path: str) -> str:
    """
    Liest Text aus einer PDF-Datei.
    Wenn kein Text erkannt wird, wird OCR auf jeder Seite durchgeführt.
    """
    try:
        reader = PdfReader(file_path)
        text_parts = []

        for page_num, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text()
            if page_text and page_text.strip():
                text_parts.append(f"--- Seite {page_num} ---\n{page_text.strip()}")
            else:
                # Seite enthält keinen Text → OCR
                ocr_text = _ocr_pdf_page(page)
                if ocr_text:
                    text_parts.append(f"--- Seite {page_num} (OCR) ---\n{ocr_text.strip()}")

        if not text_parts:
            return "Kein Text gefunden."

        return "\n\n".join(text_parts)

    except Exception as e:
        return f"Fehler beim Lesen der PDF: {e}"


def _ocr_pdf_page(page) -> str:
    """
    Führt OCR auf einer einzelnen PDF-Seite durch.
    Wandelt die Seite in ein Bild um und gibt den erkannten Text zurück.
    """
    try:
        # Versuche, Bilder aus der Seite zu extrahieren
        for image_file in page.images:
            image_bytes = image_file.data
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image, lang="deu+eng")
            if text.strip():
                return text
        return ""
    except Exception as e:
        return f"[OCR-Fehler: {e}]"
