# DocumentTextAnalyzer

Eine lokale Windows-Anwendung zur Texterkennung aus Dokumenten.

## Unterstützte Dateitypen

| Typ | Verarbeitung |
|---|---|
| PDF (mit Text) | Direkte Textextraktion |
| PDF (gescannt) | OCR |
| JPG / PNG / TIFF | OCR |
| DOCX | Text direkt lesen |
| XLSX | Zellinhalte lesen |
| PPTX | Folientexte lesen |

## Installation

### 1. Virtuelle Umgebung aktivieren
```powershell
.venv\Scripts\Activate.ps1
```

### 2. Abhängigkeiten installieren
```powershell
pip install -r requirements.txt
```

### 3. Tesseract OCR installieren (für Bilder und gescannte PDFs)
- Download: https://github.com/UB-Mannheim/tesseract/wiki
- Deutsch-Sprachpaket (deu.traineddata) mitinstallieren
- Tesseract zum Windows PATH hinzufügen

## Anwendung starten

```powershell
python main.py
```

## EXE erstellen

```powershell
pyinstaller --onefile --windowed main.py
```

Die fertige EXE liegt dann in `dist/DocumentTextAnalyzer.exe`.

## Projektstruktur

```
DocumentTextAnalyzer/
├── main.py                  # Einstiegspunkt
├── requirements.txt
├── README.md
├── .gitignore
├── input/                   # Eingabedateien (wird ignoriert)
├── output/                  # Ausgabedateien (wird ignoriert)
└── src/
    ├── app.py               # GUI (customtkinter)
    ├── file_router.py       # Dateityp-Erkennung
    ├── pdf_extractor.py     # PDF-Textextraktion + OCR
    ├── image_ocr.py         # Bild-OCR
    ├── office_extractor.py  # DOCX / XLSX / PPTX
    └── clipboard.py         # Zwischenablage-Hilfsfunktionen
```
