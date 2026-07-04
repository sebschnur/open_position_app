# Codex-Review-Prompts

## 1. Zweck

Dieses Dokument enthält Prompts für **Codex als Code-Reviewer**.

Rollenverteilung:

```text
Claude Code = Implementierung
Codex       = Review, Plausibilitätsprüfung, Qualitätssicherung
```

Codex soll nicht primär neue Features bauen, sondern prüfen:

```text
Ist die Implementierung fachlich korrekt?
Ist sie einfach genug?
Ist sie sauber strukturiert?
Gibt es riskante Fehlinterpretationen?
```

## 2. Allgemeiner Review-Prompt

Diesen Prompt bei jedem Review verwenden:

```text
Du bist Codex und reviewst eine von Claude Code erstellte Python-/Streamlit-/SQLite-Anwendung.

Bitte lies zuerst die Spezifikationsdateien:
- README.md
- 00_projektauftrag.md
- 01_fachliche_funktionen.md
- 02_datenmodell_sqlite.md
- 03_streamlit_ui_konzept.md
- 04_workflows_automatisierungen.md
- 05_umsetzungsplan_codex_claude.md
- 06_excel_mockdaten_import.md
- 07_projektstruktur_claude_code.md
- 08_claude_code_prompts.md
- 09_codex_review_prompts.md
- 10_agent_workflow.md

Review-Ziel:
Prüfe, ob die Umsetzung zur Spezifikation passt.

Bitte liefere dein Review in dieser Struktur:
1. Gesamturteil
2. Blocker
3. Hohe Risiken
4. Mittlere Hinweise
5. Kleine Verbesserungen
6. Positive Punkte
7. Konkrete nächste Fixes für Claude Code

Wichtig:
- Nenne konkrete Dateien/Funktionen, wenn möglich.
- Erfinde keine Anforderungen, die nicht in der Spezifikation stehen.
- Achte besonders auf fachliche Vorzeichenlogik, Limitprüfung, Triggerlogik und Nicht-Automatisierung.
- Schlage keine unnötig große Enterprise-Architektur vor.
- Bewerte pragmatisch für einen Prototypen.
```

## 3. Review-Checkliste: fachliche Kernregeln

Codex soll insbesondere diese Regeln prüfen:

| Bereich | Review-Frage |
|---|---|
| Vorzeichenlogik | Ist positive Menge überall `Partner kauft von uns`? |
| Vorzeichenlogik | Ist negative Menge überall `Partner verkauft an uns`? |
| Position | Wird auf der Position-Seite auf Kauf/Verkauf-Begriffe verzichtet? |
| Position | Wird PMS-Position plus untertägige Geschäfte korrekt addiert? |
| Limit | Wird je Kalenderjahr auf Absolutwert gegen 1,00 MW geprüft? |
| Schaltjahr | Wird 8.784 statt 8.760 Stunden verwendet? |
| Preise | Wird finaler Preis als Marktpreis + OTC-Aufschlag berechnet? |
| Preise | Wird Chattext ohne Settlement-Differenz erzeugt? |
| Preise | Wird Mailtext mit Settlement-Differenz erzeugt? |
| Limitorder | Wird Trigger-Preis korrekt verwendet? |
| Limitorder | Wird ausgelöste Order nur hervorgehoben, nicht automatisch ausgeführt? |
| Limitorder | Erzeugt erst Button „Ausgeführt“ ein untertägiges Geschäft? |
| Handelskalender | Werden fällige/überfällige Einträge korrekt angezeigt? |
| Handelskalender | Erzeugt erst Button „Erledigt“ ein untertägiges Geschäft? |
| SQLite | Wird bestehende DB nicht stillschweigend überschrieben? |
| Backup | Wird initiales Backup erzeugt? |
| UI | Gibt es keinen Reset-Button? |
| Tests | Ist Kernlogik ohne Streamlit testbar? |

## 4. Review-Prompt nach Arbeitspaket 1: Struktur

```text
Reviewe nur die Projektstruktur und die leere Streamlit-App.

Prüfe:
- Sind UI, Services, Repositories, Domain und DB sinnvoll getrennt?
- Startet `streamlit run app.py`?
- Gibt es genau die vier fachlichen Seiten?
- Gibt es keine unnötige Startseite mit eigener Fachlogik?
- Ist README für Setup und Start verständlich?
- Ist die Struktur für einen Prototypen angemessen einfach?

Liefere nur Findings, die für diesen frühen Stand relevant sind.
```

## 5. Review-Prompt nach Arbeitspaket 2: DB

```text
Reviewe Datenbankmodell und Initialisierung.

Prüfe:
- Stimmen Tabellen und Felder mit `02_datenmodell_sqlite.md` überein?
- Werden Mengen in MWh gespeichert und MW nur berechnet?
- Gibt es keine unnötige Historisierung?
- Wird `app.db` erzeugt?
- Wird `app_initial_backup.db` nach Seed erzeugt?
- Wird eine vorhandene DB nicht stillschweigend überschrieben?
- Ist SQLAlchemy sauber gekapselt?
- Greifen Streamlit-Seiten nicht direkt chaotisch auf die DB zu?

Bewerte pragmatisch für einen Prototypen.
```

## 6. Review-Prompt nach Arbeitspaket 3: Domain-Logik

```text
Reviewe Domain-Logik und Tests.

Prüfe besonders:
- Schaltjahrlogik korrekt?
- Stunden je Jahr korrekt?
- MWh/MW-Umrechnung korrekt?
- Rundungsregeln korrekt?
- Limitprüfung auf Absolutwert korrekt?
- Positive Menge = Partner kauft von uns?
- Negative Menge = Partner verkauft an uns?
- Limitorder-Vorzeichenvalidierung korrekt?
- Handelskalender-Vorzeichenvalidierung korrekt?
- Tests unabhängig vom echten Tagesdatum, soweit sinnvoll?

Nenne konkrete Testfälle, die fehlen.
```

## 7. Review-Prompt nach Arbeitspaket 4: Position

```text
Reviewe Position-Service und Position-Seite.

Prüfe:
- Anzeige Y0 bis Y+4?
- PMS-Position separat sichtbar?
- Untertägige Geschäfte separat sichtbar?
- Simulierte Position = PMS + untertägige Geschäfte?
- Limit 1,00 MW je Jahr?
- Limitprüfung auf Absolutwert?
- Keine Kauf/Verkauf-Begriffe auf der Position-Seite?
- Untertägige Geschäfte haben kein Richtungsfeld?
- Löschen funktioniert ohne unbeabsichtigte Seiteneffekte?
- Nach Einfügen/Löschen wird neu berechnet?

Prüfe auch, ob die UI trotz Prototyp verständlich ist.
```

## 8. Review-Prompt nach Arbeitspaket 5: Preise

```text
Reviewe Preise-Seite und Textgenerierung.

Prüfe:
- Produkte in UI-Reihenfolge: Base Y+1, Base Y+2, Base Y+3, Peak Y+1, Peak Y+2, Peak Y+3?
- Chattext-Reihenfolge: Base Y+1, Peak Y+1, Base Y+2, Peak Y+2, Base Y+3, Peak Y+3?
- Marktpreise und Aufschläge werden gemeinsam gespeichert?
- Finaler Preis = Marktpreis + OTC-Aufschlag?
- Settlement-Differenz nur im Mailtext, nicht im Chattext?
- Keine echte E-Mail-Funktion?
- PFC-Prüfung zeigt Mittelwert, Settlement, PFC-Zeitstempel und Settlement-Zeitstempel?
- Preise auf 2 Nachkommastellen?
```

## 9. Review-Prompt nach Arbeitspaket 6: Excel-/PFC-Import

```text
Reviewe Excel- und PFC-Mockdatenimport.

Prüfe gegen `06_excel_mockdaten_import.md`:
- Werden alle Zellbereiche korrekt gelesen?
- Position Frontjahre A7:H8?
- Untertägige Geschäfte A9:H10?
- Vertriebsinfos B14:C17 und G14:H17?
- Settlement Base L14:L16?
- Handelskalender A3:M6?
- Limitorder A5:G6?
- PFC-Dateimuster YYYYMMDD_EEX_PFC_YYYY.xlsx?
- PFC-Mittelwert aus D2?
- Leeres Datum bei untertägigen Geschäften = heutiges Datum?
- Excel K/V Mapping korrekt?
- Handelskalender Kauf/Verkauf Mapping korrekt?
- Limitorder-Mockfall `Partner kauft, wenn Preis <= Limit` korrekt?
- Fehlende Peak-Settlementpreise und fehlende PFCs werden als Defaults klar markiert?
- Import überschreibt bestehende DB nicht stillschweigend?
- Gibt es ein nachvollziehbares Importprotokoll?
```

## 10. Review-Prompt nach Arbeitspaket 7: Limitorder

```text
Reviewe Limitorder-Seite und Limitorder-Service.

Prüfe:
- Trigger-Preis ist Base/Peak Y+1 bis Y+3?
- Triggerbedingung nutzt Partner kauft/verkauft Formulierungen?
- Partner kauft erzwingt positive Menge?
- Partner verkauft erzwingt negative Menge?
- Limitpreisvergleich korrekt?
- Ausgelöste Order wird nur hervorgehoben?
- Kein automatisches untertägiges Geschäft ohne Button?
- Button Ausgeführt erzeugt genau ein untertägiges Geschäft?
- Danach Status ausgeführt?
- Button Gelöscht setzt Status gelöscht?
- Statuslogik offen/ausgeführt/gelöscht/abgelaufen sauber?
```

## 11. Review-Prompt nach Arbeitspaket 8: Handelskalender

```text
Reviewe Handelskalender-Seite und Handelskalender-Service.

Prüfe:
- Anzeige ab heute plus überfällige nicht erledigte Einträge?
- Erledigte Einträge nicht in Standardansicht?
- Fälligkeit heute und Vergangenheit korrekt?
- Partner kauft erzwingt positive Menge?
- Partner verkauft erzwingt negative Menge?
- Button Erledigt erzeugt genau ein untertägiges Geschäft?
- Danach Status erledigt?
- Position wird danach aktualisiert?
```

## 12. Finaler Codex-Review-Prompt

```text
Führe einen finalen Review der gesamten Anwendung durch.

Fokus:
- fachliche Korrektheit
- Einfachheit des Prototyps
- Robustheit der Mockdaten-Initialisierung
- Trennung von UI, Service, Repository und Domain
- wichtigste Tests
- Vermeidung risiko-kritischer Vollautomatisierung
- klare Begriffe rund um Partner kauft/verkauft und Vorzeichen

Bitte bewerte:
1. Ist die App fachlich plausibel arbeitsfähig?
2. Welche Punkte müssen vor einer Demo unbedingt behoben werden?
3. Welche Punkte können später verbessert werden?
4. Welche Risiken bestehen, wenn daraus später ein produktiveres Tool werden soll?

Keine großen Refactorings vorschlagen, wenn sie für den Prototyp nicht nötig sind.
```

## 13. Erwartetes Review-Format

Codex soll möglichst konkret antworten:

```text
Gesamturteil:
...

Blocker:
1. [Datei/Funktion] Problem + warum kritisch + konkrete Empfehlung

Hohe Risiken:
...

Mittlere Hinweise:
...

Kleine Verbesserungen:
...

Positive Punkte:
...

Empfohlene nächste Claude-Code-Aufgaben:
1. ...
2. ...
3. ...
```
