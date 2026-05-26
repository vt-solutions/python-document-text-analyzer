# PHYTON UI MASTERPLAN

## Ziel

Alle neuen Phyton-Apps sollen ein einheitliches, professionelles VT-Solutions-Design verwenden.

Jede App soll sofort als Produkt von **vt-solutions GmbH / it development & consulting** erkennbar sein.

---

## Grundprinzipien

- Dunkles modernes Desktop-Design
- Klare B2B-Optik
- Große, gut lesbare Texte
- Abgerundete Buttons und Container
- Einheitliche Farben, Abstände und Schriftgrößen
- Deutsche Benutzeroberfläche
- Wiederverwendbare UI-Komponenten
- Keine App soll ihr eigenes Design neu erfinden

---

## Farbkonzept

Die verbindlichen Farben stehen in:

```text
/design/theme.json
```

Wichtige Rollen:

- Hintergrund: sehr dunkles Blau/Schwarz
- Header/Footer: dunkles Navy
- Panels: dunkles Blau
- Rahmen: helles Blau
- Primäraktionen: kräftiges Blau
- Positive Aktionen: Grün
- Gefährliche Aktionen: Rot
- Text: Weiß oder helles Blau

---

## Standard-Layout

Jede Desktop-App soll grundsätzlich so aufgebaut sein:

```text
┌──────────────────────────────────────────────┐
│ Header: Logo | App-Titel | Modus | Hilfe     │
├──────────────────────────────────────────────┤
│ Hauptbereich                                 │
│                                              │
│ Primärbutton                                 │
│ Eingabe-/Drop-Zone                           │
│ Ergebnis-/Arbeitsbereich                     │
│                                              │
│ Aktionsbuttons                               │
├──────────────────────────────────────────────┤
│ Footer: Firma | Support | Website | Version │
└──────────────────────────────────────────────┘
```

---

## Header-Regeln

Der Header enthält:

- Logo links
- App-Titel
- Untertitel
- Theme-Umschalter
- Hilfe-Button

Wichtig:

- Titel und Untertitel dürfen nie abgeschnitten werden.
- Buttons dürfen den Titelbereich nicht überdecken.
- Bei kleiner Fensterbreite muss Text umbrechen oder das Fenster eine Mindestbreite haben.
- Keine festen Breiten verwenden, die Texte abschneiden.
- Lange App-Namen dürfen nicht mit `...` verschwinden, außer es ist ausdrücklich gewünscht.

---

## Buttons

### Primärbutton

Verwendung für Hauptaktionen:

- Datei auswählen
- Starten
- Verarbeiten
- Exportieren

Farbe: Blau

### Erfolgsbutton

Verwendung für positive Aktionen:

- Kopieren
- Übernehmen
- Speichern erfolgreich

Farbe: Grün

### Sekundärbutton

Verwendung für neutrale Aktionen:

- Text speichern
- Einstellungen
- Zurück

Farbe: Dunkles Navy

### Gefahrenbutton

Verwendung für irreversible Aktionen:

- Löschen
- Leeren
- Zurücksetzen

Farbe: Rot

---

## Container und Panels

- Panels haben dunklen Hintergrund
- Rahmen in Akzentblau
- Ecken sind deutlich abgerundet
- Innenabstand ist großzügig
- Keine engen oder überladenen Layouts

---

## Typografie

- Standardschrift: Segoe UI oder systemnahe Sans-Serif-Schrift
- App-Titel: groß und fett
- Untertitel: kleiner, hellblau
- Normaltext: weiß oder hellblau
- Platzhalter: gedämpftes Blau

---

## Wiederverwendbare Komponenten

Neue Apps sollen folgende Komponenten nutzen:

```text
/components/common_ui.py
```

Verbindliche Komponenten:

- `Theme`
- `VTHeader`
- `VTFooter`
- `VTButton`
- `VTPanel`
- `VTDropZone`
- `VTTextPanel`
- `create_main_window`
- `apply_theme`

---

## Responsive-/Sichtbarkeitsregeln

Pflichtregeln:

- Keine abgeschnittenen Texte
- Keine überlappenden Elemente
- Mindestfenstergröße setzen
- Header mit Grid/Flex-Logik aufbauen
- Textbereiche müssen mitwachsen
- Buttons müssen genug Breite für deutsche Texte haben
- Fenstergröße muss getestet werden:
  - 1280 × 720
  - 1366 × 768
  - 1440 × 900
  - 1920 × 1080

---

## Standard-Footer

Footer-Text:

```text
vt-solutions GmbH | support@vt-solutions.de | www.vt-solutions.de | Version 1.0.0
```

Version pro App anpassen.

---

## KI-Anweisung für neue Apps

Diese Anweisung jeder KI geben:

```text
Erstelle die App im bestehenden Phyton-/VT-Solutions-Design.

Lies zuerst:
/design/PHYTON_UI_MASTERPLAN.md
/design/theme.json
/components/common_ui.py

Verwende die vorhandenen Farben, Abstände, Buttons, Panels, Header und Footer.
Erfinde kein neues Design.
Alle Texte müssen vollständig sichtbar sein.
Das Layout muss bei normalen Desktop-Fenstergrößen sauber funktionieren.
```
