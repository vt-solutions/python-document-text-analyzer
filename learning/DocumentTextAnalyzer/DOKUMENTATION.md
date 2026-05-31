# VT Document Text Converter – Anwender-Dokumentation

**vt-solutions GmbH** · support@vt-solutions.de · www.vt-solutions.de  
Version 1.0.0 · Stand: Mai 2026

---

## Inhaltsverzeichnis

1. [Lizenz-System](#1-lizenz-system)
2. [Lizenzdatei (JSON)](#2-lizenzdatei-json)
3. [Neue EXE erstellen (Build)](#3-neue-exe-erstellen-build)
4. [Programm auf anderem PC installieren](#4-programm-auf-anderem-pc-installieren)

---

## 1. Lizenz-System

### Wie funktioniert die Lizenz?

Das Programm kennt drei Zustände:

| Zustand | Anzeige im Footer | Beschreibung |
|---|---|---|
| **Erster Start** | – | Lizenz-Dialog öffnet sich automatisch |
| **Testversion** | `🔑 Testversion · noch X Tage` | 30 Tage voll funktionsfähig |
| **PRO-Lizenz** | `🔑 PRO · Firmenname` | Dauerhaft aktiviert |
| **Abgelaufen** | `🔑 Testversion abgelaufen` | Lizenz-Dialog öffnet sich automatisch |

---

### 1.1 Testversion starten

1. Programm starten → Lizenz-Dialog erscheint automatisch
2. Rechte Seite: Schaltfläche **„▶ 30-Tage-Testversion starten"** klicken
3. Das Programm öffnet sich sofort — alle Funktionen für 30 Tage freigeschaltet

---

### 1.2 PRO-Lizenz aktivieren

1. Lizenz-Dialog öffnen:
   - Beim ersten Start: erscheint automatisch
   - Während der Nutzung: Footer → Schaltfläche **„🔑 Lizenz"** klicken
2. Linke Seite ausfüllen:
   - **Firmenname** eingeben (z. B. `Mustermann GmbH`)
   - **Lizenzschlüssel** eingeben (Format: `VT-YYYY-XXXX-XXXX`)
3. Schaltfläche **„🔑 Lizenz aktivieren"** klicken
4. Bei Erfolg: grüne Bestätigung erscheint, Programm öffnet sich

> **Lizenz anfragen:**  
> E-Mail an support@vt-solutions.de  
> Betreff: `VT Converter PRO Lizenz`

---

### 1.3 Lizenz-Status zurücksetzen (für Tests)

Um den Lizenz-Dialog erneut anzuzeigen (z. B. für Tests):

**Option A – Datei-Explorer:**
```
C:\Users\<IhrName>\AppData\Roaming\vt-solutions\VTConverter\
```
→ Datei `license.json` löschen  
→ Programm neu starten → Lizenz-Dialog erscheint wieder

**Option B – Eingabeaufforderung (CMD):**
```
del "%APPDATA%\vt-solutions\VTConverter\license.json"
```

---

## 2. Lizenzdatei (JSON)

### Wo liegt die Datei?

```
C:\Users\<IhrName>\AppData\Roaming\vt-solutions\VTConverter\license.json
```

> `AppData` ist ein versteckter Ordner.  
> Im Explorer: Oben in der Adressleiste `%APPDATA%\vt-solutions\VTConverter` eingeben → Enter

---

### Inhalt der Lizenzdatei

**Testversion (Beispiel):**
```json
{
  "customer": "Testbenutzer",
  "license_key": "TRIAL",
  "activated": false,
  "edition": "TRIAL",
  "trial_started": "2026-05-26T16:32:54.533300",
  "trial_ends": "2026-06-25T16:32:54.533327"
}
```

**PRO-Lizenz (Beispiel):**
```json
{
  "customer": "Mustermann GmbH",
  "license_key": "VT-2026-ABCD-1234",
  "activated": true,
  "edition": "PRO",
  "activated_at": "2026-05-26T10:00:00.000000"
}
```

---

### Bedeutung der Felder

| Feld | Bedeutung |
|---|---|
| `customer` | Eingegebener Firmenname |
| `license_key` | Lizenzschlüssel oder `TRIAL` |
| `activated` | `true` = PRO-Lizenz aktiv |
| `edition` | `TRIAL` oder `PRO` |
| `trial_started` | Startzeitpunkt der Testversion |
| `trial_ends` | Ablaufdatum der Testversion |

> **Wichtig:** Die Datei nicht manuell bearbeiten — das Programm erkennt manipulierte Einträge.

---

## 3. Neue EXE erstellen (Build)

### Voraussetzungen (einmalig)

| Software | Download |
|---|---|
| Python 3.11+ | https://www.python.org/downloads/ |
| Inno Setup 6 | https://jrsoftware.org/isdl.php |
| Virtual Environment | wird automatisch erstellt |

---

### Build-Prozess (Schritt für Schritt)

**1. VS Code öffnen**  
Projektordner: `C:\Users\VyacheslavTsoy\PythonProjects\learning\DocumentTextAnalyzer`

**2. Terminal öffnen**  
`Strg + ö`  oder  Menü → Terminal → Neues Terminal

**3. Build starten:**
```
cmd /c .\build.bat
```

**4. Warten** — der Build läuft automatisch durch 5 Schritte:

```
[1/5] Alte Artefakte bereinigen ...
[2/5] Installer-Bilder generieren ...
[3/5] PyInstaller startet ...        ← dauert 1-3 Minuten
[4/5] EXE pruefen ...
[5/5] Installer bauen (Inno Setup) ...
```

**5. Ergebnis:**

| Datei | Beschreibung |
|---|---|
| `dist\VT_Document_Text_Converter.exe` | Einzelne EXE (portabel, kein Installer) |
| `installer_output\VT_Document_Text_Converter_Setup_v1.0.0.exe` | Setup-Installer für andere PCs |

**6. Am Ende:**  
```
Ausgabeordner oeffnen? [j/n]:
```
→ `j` eingeben → Explorer öffnet sich mit der fertigen Setup-Datei

---

### Wann muss ich neu bauen?

| Situation | Neu bauen? |
|---|---|
| Code geändert (app.py, etc.) | **Ja** |
| Neue Funktionen hinzugefügt | **Ja** |
| Nur Texte/Farben geändert | **Ja** |
| Lizenz-JSON gelöscht | Nein |
| Auf gleichem PC testen | Nein – direkt `python main.py` |

---

## 4. Programm auf anderem PC installieren

### Was wird benötigt?

Nur **eine Datei:**
```
VT_Document_Text_Converter_Setup_v1.0.0.exe
```
Diese liegt nach dem Build in:
```
installer_output\VT_Document_Text_Converter_Setup_v1.0.0.exe
```

> Kein Python, kein VS Code, keine weiteren Programme auf dem Ziel-PC nötig.

---

### Installation auf dem Ziel-PC

**Schritt 1:** Setup-Datei auf den Ziel-PC kopieren  
(USB-Stick, Netzlaufwerk, E-Mail, Cloud-Speicher)

**Schritt 2:** Doppelklick auf `VT_Document_Text_Converter_Setup_v1.0.0.exe`

**Schritt 3:** UAC-Dialog bestätigen („Ja" klicken)

**Schritt 4:** Installations-Assistent folgen:

```
┌─────────────────────────────────────────┐
│  Willkommen                             │  ← Weiter klicken
├─────────────────────────────────────────┤
│  Installationspfad auswählen            │  ← Standard oder eigenen Pfad wählen
│  C:\Program Files\VT Document Text...  │
├─────────────────────────────────────────┤
│  Startmenü-Gruppe                       │  ← So lassen oder umbenennen
├─────────────────────────────────────────┤
│  Zusätzliche Symbole                    │  ← Desktop-Verknüpfung: Ja/Nein
├─────────────────────────────────────────┤
│  Installation läuft ...                 │  ← automatisch
├─────────────────────────────────────────┤
│  Fertig! Programm jetzt starten?        │  ← Haken setzen → Fertig stellen
└─────────────────────────────────────────┘
```

**Schritt 5:** Beim ersten Start erscheint der **Lizenz-Dialog**  
→ Testversion starten oder Lizenzschlüssel eingeben

---

### Systemanforderungen Ziel-PC

| Anforderung | Minimum |
|---|---|
| Betriebssystem | Windows 10 / 11 (64-Bit) |
| Arbeitsspeicher | 4 GB RAM |
| Festplatte | 150 MB frei |
| Rechte | Administratorrechte für Installation |
| Internet | Nicht erforderlich (100 % lokal) |

---

### Deinstallation auf dem Ziel-PC

**Option A – Einstellungen:**  
Windows-Einstellungen → Apps → `VT Document Text Converter` → Deinstallieren

**Option B – Startmenü:**  
Startmenü → `VT Document Text Converter` → `VT Document Text Converter deinstallieren`

> Beim Deinstallieren wird das Programm entfernt.  
> Die Lizenzdatei unter `%APPDATA%\vt-solutions\VTConverter\` bleibt erhalten.

---

## Schnellreferenz

| Aufgabe | Befehl / Ort |
|---|---|
| Programm starten (Entwicklung) | `python main.py` im Terminal |
| Neue EXE + Installer bauen | `cmd /c .\build.bat` im Terminal |
| Lizenzdatei öffnen | `%APPDATA%\vt-solutions\VTConverter\license.json` |
| Lizenz zurücksetzen | Lizenzdatei löschen → Programm neu starten |
| Lizenz anfragen | support@vt-solutions.de |
| Setup-Datei für andere PCs | `installer_output\VT_Document_Text_Converter_Setup_v1.0.0.exe` |

---

*© 2026 vt-solutions GmbH · Alle Rechte vorbehalten*
