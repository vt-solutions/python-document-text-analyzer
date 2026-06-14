"""
image_ocr.py
Führt OCR auf Bilddateien durch (JPG, PNG, TIFF, BMP usw.).
Verwendet pytesseract mit Deutsch + Englisch als Standardsprachen.
"""

import pytesseract
from PIL import Image

import src.ocr_config  # setzt pytesseract.tesseract_cmd  # noqa: F401


def extract_image_ocr(file_path: str, lang: str = "deu+eng") -> str:
    """
    Erkennt Text in einer Bilddatei mittels OCR.

    Args:
        file_path: Pfad zur Bilddatei
        lang: Tesseract-Sprache(n), Standard: Deutsch + Englisch

    Returns:
        Erkannter Text als String
    """
    try:
        image = Image.open(file_path)

        # Bild vorverarbeiten: Graustufen verbessert OCR-Genauigkeit
        image = image.convert("L")

        text = pytesseract.image_to_string(image, lang=lang)

        if not text.strip():
            return "Kein Text erkannt. Bitte prüfe die Bildqualität."

        return text.strip()

    except pytesseract.TesseractNotFoundError:
        return (
            "Tesseract OCR nicht gefunden!\n\n"
            "Bitte installiere Tesseract:\n"
            "https://github.com/UB-Mannheim/tesseract/wiki\n\n"
            "Nach der Installation entweder:\n"
            "1. Tesseract zum Windows PATH hinzufügen, oder\n"
            "2. In src/image_ocr.py den Pfad manuell setzen."
        )
    except Exception as e:
        return f"Fehler bei der OCR-Verarbeitung: {e}"
