# -*- mode: python ; coding: utf-8 -*-
"""
VT_Converter.spec
PyInstaller Spec-Datei fuer VT Document Text Converter.
Build: pyinstaller VT_Converter.spec
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

SPEC_DIR = os.path.dirname(os.path.abspath(SPEC))
VENV_SITE = os.path.join(SPEC_DIR, '.venv', 'Lib', 'site-packages')

# ── Paket-Daten und Untermodule sammeln ──────────────────────────────── #
customtkinter_datas  = collect_data_files('customtkinter')
tkinterdnd2_datas    = collect_data_files('tkinterdnd2')
reportlab_datas      = collect_data_files('reportlab')   # Schriften & Templates

reportlab_submodules = collect_submodules('reportlab')   # viele dynamische Importe
odf_submodules       = collect_submodules('odf')         # odfpy: alle Untermodule

block_cipher = None

a = Analysis(
    [os.path.join(SPEC_DIR, 'main.py')],
    pathex=[SPEC_DIR, VENV_SITE],
    binaries=[],
    datas=[
        # App-Assets (Logo, Icon)
        (os.path.join(SPEC_DIR, 'assets'), 'assets'),
        # Pakete mit Nicht-Python-Dateien
        *customtkinter_datas,
        *tkinterdnd2_datas,
        *reportlab_datas,
    ],
    hiddenimports=[
        # ── GUI ────────────────────────────────────────────────────────
        'customtkinter',
        'tkinterdnd2',

        # ── Bild / OCR ─────────────────────────────────────────────────
        'PIL', 'PIL._imaging', 'PIL.Image', 'PIL.ImageTk', 'PIL.ImageOps',
        'PIL.ImageDraw', 'PIL.ImageFont',
        'pytesseract',

        # ── PDF ────────────────────────────────────────────────────────
        'pypdf', 'pypdf._reader', 'pypdf._writer',

        # ── Office (DOCX / XLSX / PPTX) ────────────────────────────────
        'docx', 'docx.oxml', 'docx.oxml.ns',
        'docx.shared', 'docx.enum.text', 'docx.enum.table',
        'openpyxl', 'openpyxl.styles', 'openpyxl.workbook',
        'pptx', 'pptx.util',

        # ── PRO: ODT (odfpy) ───────────────────────────────────────────
        # Delayed-Import in pro_extractor.py → muss explizit gelistet sein
        'odf', 'odf.opendocument', 'odf.text', 'odf.element',
        *odf_submodules,

        # ── PRO: RTF (striprtf) ────────────────────────────────────────
        # Delayed-Import in pro_extractor.py
        'striprtf', 'striprtf.striprtf',

        # ── PRO: PDF-Export (reportlab) ────────────────────────────────
        # Delayed-Import in pro_exporter.py
        'reportlab',
        'reportlab.lib', 'reportlab.lib.pagesizes', 'reportlab.lib.styles',
        'reportlab.lib.units', 'reportlab.lib.colors', 'reportlab.lib.enums',
        'reportlab.platypus',
        'reportlab.platypus.paragraph', 'reportlab.platypus.flowables',
        'reportlab.pdfgen', 'reportlab.pdfgen.canvas',
        'reportlab.pdfbase', 'reportlab.pdfbase.pdfmetrics',
        'reportlab.pdfbase.ttfonts',
        *reportlab_submodules,

        # ── Eigene App-Module ──────────────────────────────────────────
        'src', 'src.app', 'src.version', 'src.file_router',
        'src.pdf_extractor', 'src.image_ocr', 'src.office_extractor',
        'src.ocr_config',    # zentrale Tesseract-Pfadkonfiguration
        'src.clipboard', 'src.settings_manager', 'src.theme',

        # PRO-Module: delayed import (innerhalb von Funktionen/if-Bloecken)
        'src.pro_extractor',   # import in file_router.py (if allow_pro)
        'src.pro_exporter',    # import in app.py (_save_as_docx / _save_as_pdf)
        'src.pro_batch',       # import in batch_dialog.py

        # UI-Module
        'src.ui', 'src.ui.info_dialog', 'src.ui.license_dialog',
        'src.ui.batch_dialog',

        # Lizenz-Module
        'src.licensing', 'src.licensing.license_manager',
        'src.licensing.license_crypto',   # neu: HMAC-Validierung
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'numpy', 'scipy', 'pandas',
        'notebook', 'IPython', 'docx as create_docs',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VT_Document_Text_Converter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,               # Kein schwarzes Konsolenfenster
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(SPEC_DIR, 'assets', 'app.ico'),
)
