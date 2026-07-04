# Projektauftrag: Excel-Ablösung als Python-/Streamlit-Prototyp

## 1. Ziel

Ziel ist die strukturierte Ablösung einer bestehenden Excel-/VBA-Datei durch einen Prototypen auf Basis von:

- Python
- Streamlit
- SQLite
- SQLAlchemy
- Mock-Daten

Der Prototyp soll die wesentlichen Funktionen der Excel-Datei möglichst vollständig abbilden. Überflüssige Nebenfunktionen können entfallen, sofern sie für den fachlichen Kernprozess nicht erforderlich sind.

## 2. Charakter des Prototyps

Der Prototyp ist keine produktive Enterprise-Anwendung. Er soll aber fachlich so plausibel und vollständig wirken, dass ein kleiner fachkundiger Nutzerkreis damit testweise arbeiten könnte.

Der Prototyp soll insbesondere zeigen:

- wie die aktuelle offene Position berechnet und angezeigt wird
- wie untertägige Geschäfte erfasst werden
- wie die Limitauslastung je Kalenderjahr geprüft wird
- wie Marktpreise und OTC-Aufschläge gepflegt werden
- wie Preis-Texte für Vertriebskommunikation erzeugt werden
- wie Limitorders geprüft und abgearbeitet werden
- wie Handelskalendereinträge gepflegt und erledigt werden
- wie aus erledigten Limitorders oder Handelskalendereinträgen untertägige Geschäfte entstehen

## 3. Zielgruppe

Der Nutzerkreis besteht aus ca. 6 Personen:

- fachlich kompetente Nutzer aus dem Energievertrieb/-handel
- IT-affine Anwender
- teilweise Personen mit Programmierkenntnissen

Daher ist keine hochpolierte Usability erforderlich. Eine klare, einfache und fachlich nachvollziehbare Oberfläche reicht aus.

## 4. Nicht-Ziele

Der Prototyp soll bewusst nicht leisten:

- keine echte Vollautomatisierung risiko-kritischer Handelsentscheidungen
- kein automatischer Marktabschluss
- kein echter E-Mail-Versand
- keine komplexe Benutzer- und Rechteverwaltung
- keine revisionssichere Historisierung
- kein produktiver Anschluss an echte Markt-/Portfolio-/EEX-Schnittstellen
- keine zentrale PostgreSQL-Produktionsdatenbank im ersten Schritt
- kein perfektes UI wie eine professionelle Webanwendung

## 5. Wichtige fachliche Leitplanke

Die Anwendung ist ein Entscheidungs- und Arbeitsunterstützungssystem.

Sie darf anzeigen, berechnen, hervorheben und Textvorschläge erzeugen. Die finale fachliche Entscheidung bleibt beim Nutzer.

```text
Die Anwendung sagt:
"Diese Position, Order oder Kalenderaktion braucht Aufmerksamkeit."

Sie sagt nicht:
"Ich führe automatisch ein Handelsgeschäft aus."
```

## 6. Technischer Ziel-Stack

| Komponente | Zweck |
|---|---|
| Python | fachliche Logik, Berechnung, Workflows |
| Streamlit | einfache UI, Tabellen, Formulare, Buttons, Texte |
| SQLite | lokale Mock-Datenbank im Prototyp |
| SQLAlchemy | Datenbankabstraktion, späterer Wechsel zu PostgreSQL möglich |
| pandas | tabellarische Verarbeitung und Anzeige |

## 7. Mock-Datenstrategie

Die SQLite-Datenbank ist im Prototyp die zentrale Mock-Datenschicht.

Sie ersetzt zunächst:

- Excel-Export aus dem Portfoliomanagementsystem
- spätere API-Anbindung
- spätere zentrale PostgreSQL-Datenbank
- Settlement-Dateiimport
- PFC-Dateiimport
- aktuelle Marktpreisquelle

Die Anwendung soll fachlich nicht direkt von Excel-Dateien abhängen, sondern über strukturierte Datenbanktabellen arbeiten.

## 8. Persistenzstrategie

- Eingaben werden dauerhaft in SQLite gespeichert.
- Es gibt keine Historisierung.
- Es gibt kein Änderungslog.
- Es gibt keinen Reset-Button in der App.
- Es soll eine initiale Backup-Datei der SQLite-Datenbank geben.

Empfohlene Struktur:

```text
data/
  app.db                 # aktive SQLite-Datenbank
  app_initial_backup.db  # initialer Mock-Datenstand als Backup
```

## 9. Initiale Datenbefüllung

Die SQLite-Datenbank soll vor dem Start mit Mock-Daten befüllt werden.

Strategie:

1. Wenn `data/app.db` existiert und Daten enthält, wird sie verwendet.
2. Wenn sie leer ist oder nicht existiert, wird sie initialisiert.
3. Start-Mock-Daten sollen aus einer vorbereiteten Excel-Datei gelesen werden.
4. Falls Werte fehlen, sollen sinnvolle Defaults genutzt oder fehlende Werte abgefragt werden.
5. Nach Initialisierung wird eine Backup-Kopie als `app_initial_backup.db` erzeugt.

Hinweis: Die konkrete Zuordnung der Excel-Felder erfolgt in einem späteren Schritt, sobald eine bereinigte Excel-Datei mit Mock-Daten bereitgestellt wird.

## 10. Jahreslogik

Die App bestimmt das aktuelle Jahr automatisch aus dem heutigen Datum.

- Positionen: aktuelles Jahr bis Y+4
- Preise: Y+1 bis Y+3

Beispiel bei aktuellem Jahr 2026:

| Bereich | Jahre |
|---|---|
| Position | 2026, 2027, 2028, 2029, 2030 |
| Preise | 2027, 2028, 2029 |

## 11. Rundungsregeln

| Werttyp | Rundung |
|---|---:|
| Preise | 2 Nachkommastellen |
| Mengen in MWh | 0 Nachkommastellen |
| Mengen in MW | 2 Nachkommastellen |
