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

:: Python aus venv verwenden
set PYTHON=.venv\Scripts\python.exe
set PIP=.venv\Scripts\pip.exe
set PYINSTALLER=.venv\Scripts\pyinstaller.exe

if not exist "%PYTHON%" (
    echo [FEHLER] venv nicht gefunden: %PYTHON%
    echo         Bitte zuerst:  python -m venv .venv
    pause
    exit /b 1
)

echo [OK] Python: %PYTHON%

"%PYTHON%" -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo [INFO] PyInstaller nicht gefunden - wird installiert ...
    "%PIP%" install pyinstaller
)

:: [1/5] Alte Artefakte bereinigen
echo.
echo [1/5] Alte Artefakte bereinigen ...

if exist "dist\VT_Document_Text_Converter.exe" (
    del /f /q "dist\VT_Document_Text_Converter.exe"
    echo       dist\VT_Document_Text_Converter.exe entfernt
)

if exist "build" (
    rmdir /s /q "build"
    echo       build\ entfernt
)

if exist "installer_output" (
    rmdir /s /q "installer_output"
    echo       installer_output\ entfernt
)

for /d /r . %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d"
)
echo       __pycache__ bereinigt

:: [2/5] Wizard-Bilder generieren
echo.
echo [2/5] Installer-Bilder generieren ...
"%PYTHON%" installer\make_wizard_images.py
if errorlevel 1 (
    echo [WARNUNG] Wizard-Bilder konnten nicht erstellt werden - wird fortgesetzt.
)

:: [3/5] EXE bauen
echo.
echo [3/5] PyInstaller startet ...
echo.

"%PYINSTALLER%" VT_Converter.spec --noconfirm

if errorlevel 1 (
    echo.
    echo [FEHLER] EXE-Build fehlgeschlagen!
    pause
    exit /b 1
)

:: [4/5] EXE pruefen
echo.
echo [4/5] EXE pruefen ...

set EXE=dist\VT_Document_Text_Converter.exe
if not exist "%EXE%" (
    echo [FEHLER] EXE nicht gefunden: %EXE%
    pause
    exit /b 1
)

for %%f in ("%EXE%") do set SIZE=%%~zf
set /a SIZE_MB=!SIZE! / 1048576
echo       EXE: %EXE%  (~!SIZE_MB! MB)

:: [5/5] Installer bauen (Inno Setup)
echo.
echo [5/5] Installer bauen (Inno Setup) ...

set ISCC=
if exist "C:\Program Files (x86)\Inno Setup 6\iscc.exe" set ISCC=C:\Program Files (x86)\Inno Setup 6\iscc.exe
if exist "C:\Program Files\Inno Setup 6\iscc.exe" set ISCC=C:\Program Files\Inno Setup 6\iscc.exe
where iscc >nul 2>&1 && if "!ISCC!"=="" set ISCC=iscc

if "!ISCC!"=="" (
    echo [INFO] Inno Setup 6 nicht gefunden - Installer wird uebersprungen.
    echo        https://jrsoftware.org/isdl.php
    goto :done
)

if not exist "installer_output" mkdir "installer_output"

"!ISCC!" "installer\VT_Converter_Setup.iss"

if errorlevel 1 (
    echo [FEHLER] Installer-Build fehlgeschlagen!
    pause
    exit /b 1
)

:: Version dynamisch aus der .iss-Datei lesen
for /f "tokens=3 delims== " %%v in ('findstr /i "AppVersion" installer\VT_Converter_Setup.iss') do set APP_VER=%%~v

set SETUP_EXE=installer_output\VT_Document_Text_Converter_Setup_v!APP_VER!.exe
if exist "!SETUP_EXE!" (
    for %%f in ("!SETUP_EXE!") do set SETUP_SIZE=%%~zf
    set /a SETUP_MB=!SETUP_SIZE! / 1048576
    echo       Setup: !SETUP_EXE!  (~!SETUP_MB! MB)
)

:done
echo.
echo ============================================================
echo   BUILD ABGESCHLOSSEN
echo.
echo   EXE:   dist\VT_Document_Text_Converter.exe
if exist "!SETUP_EXE!" (
    echo   SETUP: !SETUP_EXE!
)
echo ============================================================
echo.

set /p OPEN="Ausgabeordner oeffnen? [j/n]: "
if /i "!OPEN!"=="j" (
    if exist "!SETUP_EXE!" (
        explorer installer_output
    ) else (
        explorer dist
    )
)

endlocal
