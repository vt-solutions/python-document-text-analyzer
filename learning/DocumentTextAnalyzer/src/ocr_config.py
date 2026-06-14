"""
ocr_config.py
Zentrale Konfiguration fuer Tesseract OCR.
Einmalig importieren – setzt pytesseract.tesseract_cmd fuer den gesamten Prozess.
"""

import os
import pytesseract

pytesseract.pytesseract.tesseract_cmd = os.path.join(
    os.environ.get("ProgramFiles", r"C:\Program Files"),
    "Tesseract-OCR",
    "tesseract.exe",
)
