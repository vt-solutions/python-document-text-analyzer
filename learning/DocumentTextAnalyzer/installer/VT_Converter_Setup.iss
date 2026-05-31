; =============================================================================
;  VT_Converter_Setup.iss
;  Inno Setup 6  -  Installer-Skript fuer VT Document Text Converter
;  vt-solutions GmbH  -  support@vt-solutions.de
;
;  Build:  iscc installer\VT_Converter_Setup.iss
;  Voraussetzung: Inno Setup 6  https://jrsoftware.org/isdl.php
; =============================================================================

#define AppName        "VT Document Text Converter"
#define AppVersion     "2.0.0"
#define AppPublisher   "vt-solutions GmbH"
#define AppURL         "https://www.vt-solutions.de"
#define AppSupportURL  "mailto:support@vt-solutions.de"
#define AppExeName     "VT_Document_Text_Converter.exe"
#define AppId          "{{A3F8C2D1-5E4B-4A7F-9C3D-2B8E1A6F0D94}"

; Pfade relativ zum installer\-Ordner
#define RootDir    ".."
#define DistDir    "..\dist"
#define AssetsDir  "..\assets"
#define DepDir     "dependencies"

; Tesseract-Installer (wird mitgeliefert)
#define TesseractSetup  "tesseract-ocr-w64-setup.exe"

; =============================================================================
[Setup]
AppId={#AppId}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppSupportURL}
AppUpdatesURL={#AppURL}
AppCopyright=© 2026 vt-solutions GmbH

; Installationspfad - Benutzer waehlt selbst
DefaultDirName={autopf}\{#AppName}
DisableDirPage=no
DirExistsWarning=auto

; Startmenue
DefaultGroupName={#AppName}
DisableProgramGroupPage=no
AllowNoIcons=yes

; Ausgabe
OutputDir={#RootDir}\installer_output
OutputBaseFilename=VT_Document_Text_Converter_Setup_v{#AppVersion}
SetupIconFile={#AssetsDir}\app.ico

; Aussehen
WizardStyle=modern
WizardSmallImageFile={#AssetsDir}\wizard_small.bmp
WizardImageFile={#AssetsDir}\wizard_banner.bmp

; Kompression
Compression=lzma2/ultra64
SolidCompression=yes
InternalCompressLevel=ultra64

; Architektur
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible

; Rechte
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Sonstiges
MinVersion=10.0
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppName} Setup
VersionInfoCopyright=© 2026 vt-solutions GmbH
ShowLanguageDialog=no
LanguageDetectionMethod=uilanguage

; =============================================================================
[Languages]
Name: "german";  MessagesFile: "compiler:Languages\German.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

; =============================================================================
[CustomMessages]
german.TesseractInstalling=Tesseract OCR wird installiert (Deutsch + Englisch) ...
english.TesseractInstalling=Installing Tesseract OCR (German + English) ...

; =============================================================================
[Tasks]
Name: "desktopicon"; Description: "Desktop-Verknuepfung erstellen"; GroupDescription: "Zusaetzliche Symbole:"
Name: "quicklaunchicon"; Description: "Verkn. in Taskleiste anlegen"; GroupDescription: "Zusaetzliche Symbole:"; Flags: unchecked

; =============================================================================
[Files]
; Haupt-EXE
Source: "{#DistDir}\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion

; Tesseract Installer (temporaer in tmp-Ordner, wird nach Installation geloescht)
Source: "{#DepDir}\{#TesseractSetup}"; DestDir: "{tmp}"; Flags: deleteafterinstall

; =============================================================================
[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{group}\{#AppName} deinstallieren"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon
Name: "{commonstartmenu}\Programme\{#AppName} Schnellstart"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

; =============================================================================
[Run]
; Tesseract installieren - nur wenn noch nicht vorhanden
Filename: "{tmp}\{#TesseractSetup}"; Parameters: "/VERYSILENT /NORESTART /ALLUSERS /DIR=""C:\Program Files\Tesseract-OCR"""; StatusMsg: "{cm:TesseractInstalling}"; Check: TesseractNeeded; Flags: waituntilterminated

; Anwendung nach Installation starten (optional)
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

; =============================================================================
[UninstallDelete]
; Lizenzdaten beim Deinstallieren behalten (auskommentiert)
; Type: filesandordirs; Name: "{userappdata}\vt-solutions\VTConverter"

; =============================================================================
[Code]

{ Prueft ob Tesseract bereits installiert ist }
function TesseractNeeded: Boolean;
begin
  Result := not FileExists('C:\Program Files\Tesseract-OCR\tesseract.exe');
end;

{ Schreibrechte-Pruefung }
function IsWritable(const Dir: String): Boolean;
var
  TestFile: String;
begin
  Result   := False;
  TestFile := AddBackslash(Dir) + '._vt_write_test_';
  if SaveStringToFile(TestFile, '', False) then begin
    DeleteFile(TestFile);
    Result := True;
  end;
end;

{ Pfad-Validierung: Schreibrechte pruefen }
function NextButtonClick(CurPageID: Integer): Boolean;
var
  TargetDir: String;
begin
  Result := True;

  if CurPageID = wpSelectDir then begin
    TargetDir := WizardDirValue;

    if Trim(TargetDir) = '' then begin
      MsgBox('Bitte waehlen Sie einen Installationspfad aus.', mbError, MB_OK);
      Result := False;
      Exit;
    end;

    if not DirExists(TargetDir) then begin
      if not CreateDir(TargetDir) then begin
        if not IsWritable(ExtractFileDir(TargetDir)) then begin
          MsgBox(
            'Der gewaehlte Pfad kann nicht erstellt werden:' + #13#10 +
            TargetDir + #13#10#13#10 +
            'Bitte waehlen Sie einen anderen Pfad oder' + #13#10 +
            'starten Sie den Installer als Administrator.',
            mbError, MB_OK);
          Result := False;
          Exit;
        end;
        RemoveDir(TargetDir);
      end else begin
        RemoveDir(TargetDir);
      end;
    end else begin
      if not IsWritable(TargetDir) then begin
        MsgBox(
          'Keine Schreibrechte fuer den gewaehlten Pfad:' + #13#10 +
          TargetDir + #13#10#13#10 +
          'Bitte waehlen Sie einen anderen Pfad oder' + #13#10 +
          'starten Sie den Installer als Administrator.',
          mbError, MB_OK);
        Result := False;
        Exit;
      end;
    end;
  end;
end;

{ Deinstallations-Bestaetigung }
function InitializeUninstall(): Boolean;
begin
  Result := MsgBox(
    'Moechten Sie {#AppName} wirklich deinstallieren?',
    mbConfirmation, MB_YESNO) = IDYES;
end;
