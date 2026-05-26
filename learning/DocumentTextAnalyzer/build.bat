@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ============================================================
echo   VT Document Text Converter  -  Build-Skript
echo   vt-solutions GmbH
echo ============================================================
echo.

:: Projektverzeichnis = Verzeichnis dieser Batch-Datei
cd /d "%~dp0"

:: ─── Python + PyInstaller prüfen ─────────────────────────────────
python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden. Bitte Python installieren.
    pause & exit /b 1
)

python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller nicht gefunden – wird installiert ...
    pip install pyinstaller
)

:: ─── Alte Build-Artefakte bereinigen ─────────────────────────────
echo [1/4]  Alte Artefakte bereinigen ...

if exist "dist\VT_Document_Text_Converter.exe" (
    del /f /q "dist\VT_Document_Text_Converter.exe"
    echo       dist\VT_Document_Text_Converter.exe entfernt
)

if exist "build" (
    rmdir /s /q "build"
    echo       build\ entfernt
)

:: __pycache__ rekursiv entfernen
for /d /r . %%d in (__pycache__) do (
    if exist "%%d" (
        rmdir /s /q "%%d"
    )
)
echo       __pycache__ bereinigt

:: ─── Build ausführen ─────────────────────────────────────────────
echo.
echo [2/4]  PyInstaller startet ...
echo.

pyinstaller VT_Converter.spec --noconfirm

if errorlevel 1 (
    echo.
    echo [FEHLER] Build fehlgeschlagen!
    pause & exit /b 1
)

:: ─── Ergebnis prüfen ─────────────────────────────────────────────
echo.
echo [3/4]  Ergebnis prüfen ...

set EXE=dist\VT_Document_Text_Converter.exe
if not exist "%EXE%" (
    echo [FEHLER] EXE nicht gefunden: %EXE%
    pause & exit /b 1
)

:: Dateigröße ermitteln (für die Ausgabe)
for %%f in ("%EXE%") do set SIZE=%%~zf
set /a SIZE_MB=!SIZE! / 1048576

echo.
echo ============================================================
echo [4/4]  BUILD ERFOLGREICH!
echo.
echo   Datei:   %EXE%
echo   Groesse: ~!SIZE_MB! MB
echo ============================================================
echo.

:: Optional: Ausgabeverzeichnis öffnen
set /p OPEN="Ausgabeordner 'dist' öffnen? [j/n]: "
if /i "!OPEN!"=="j" (
    explorer dist
)

endlocal
