# Claude-Code-Prompts für die Umsetzung

## 1. Zweck

Dieses Dokument enthält konkrete Prompts für **Claude Code** als implementierenden Coding-Agenten.

Rollenverteilung:

```text
Claude Code = Implementierung
Codex       = Code Review
```

Claude Code soll nicht alle Funktionen auf einmal bauen. Besser ist eine Umsetzung in kleinen, prüfbaren Arbeitspaketen.

## 2. Allgemeine Arbeitsanweisung für Claude Code

Diesen Prompt zu Beginn im Zielrepository verwenden:

```text
Du bist Claude Code und implementierst einen Prototypen für eine interne Energiehandels-Anwendung.

Bitte lies zuerst alle Markdown-Spezifikationen im bereitgestellten Ordner:
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

Ziel:
Baue eine einfache, aber fachlich vollständige Streamlit-App mit Python, SQLite und SQLAlchemy.

Wichtige Regeln:
- Die App ist ein Prototyp mit Mockdaten.
- SQLite ist die zentrale Mock-Datenschicht.
- Verwende SQLAlchemy für alle DB-Zugriffe.
- Trenne UI, Services, Repositories und Domain-Logik.
- Streamlit-Seiten sollen keine komplexe Fachlogik enthalten.
- Es gibt vier Seiten: Position, Preise, Limitorder, Handelskalender.
- Es gibt keine separate Startseite.
- Keine echte E-Mail senden, nur kopierbare Texte erzeugen.
- Keine Handelsentscheidung automatisch ausführen.
- Limitorders werden nur hervorgehoben; erst ein Button erzeugt ein untertägiges Geschäft.
- Handelskalendereinträge erzeugen erst beim Button „Erledigt“ ein untertägiges Geschäft.
- Kein Reset-Button in der UI.
- Initiales DB-Backup nach Seed erzeugen.

Wichtigste Fachregel:
Positive Menge = Partner kauft von uns = Positionswirkung positiv.
Negative Menge = Partner verkauft an uns = Positionswirkung negativ.

Bitte arbeite in kleinen Schritten. Nach jedem Arbeitspaket:
1. Liste die geänderten Dateien auf.
2. Erkläre kurz, was implementiert wurde.
3. Nenne, welche Tests oder Startbefehle ausgeführt wurden.
4. Nenne offene Punkte oder Annahmen.
```

## 3. Prompt 1: Projektstruktur und leere App

```text
Implementiere Arbeitspaket 1: Projektstruktur und leere Streamlit-App.

Aufgabe:
- Lege eine saubere Projektstruktur gemäß `07_projektstruktur_claude_code.md` an.
- Die finale Struktur darf pragmatisch angepasst werden, muss aber UI, Services, Repositories, Domain und DB trennen.
- Lege `app.py` und vier Streamlit-Seiten an:
  - Position
  - Preise
  - Limitorder
  - Handelskalender
- Lege `requirements.txt` an.
- Nutze Python 3.12-kompatible Pakete:
  - streamlit
  - sqlalchemy
  - pandas
  - openpyxl
  - pytest
- Erstelle ein Zielprojekt-README mit Startbefehlen.

Noch nicht implementieren:
- keine Fachlogik
- keine echten Formulare
- keine Excel-Importlogik

Akzeptanzkriterien:
- `streamlit run app.py` startet.
- Alle vier Seiten sind erreichbar.
- Die Projektstruktur ist nachvollziehbar.
- README erklärt Installation und Start.
```

## 4. Prompt 2: Datenbankmodell und Initialisierung

```text
Implementiere Arbeitspaket 2: SQLAlchemy-Datenmodell und DB-Initialisierung.

Nutze `02_datenmodell_sqlite.md` als fachliche Vorgabe.

Aufgabe:
- Erstelle SQLAlchemy-Engine und Session-Handling.
- Implementiere Modelle für:
  - portfolio_positions
  - intraday_trades
  - market_prices
  - otc_surcharges
  - settlement_prices
  - pfc_checks
  - limit_orders
  - trading_calendar
  - app_metadata
- Implementiere `scripts/init_db.py`.
- Implementiere `scripts/seed_default_mock_data.py`.
- Erzeuge `data/app.db`, falls sie nicht existiert.
- Befülle eine leere DB mit plausiblen Default-Mockdaten.
- Erzeuge nach erfolgreichem Seed `data/app_initial_backup.db`.
- Überschreibe eine vorhandene DB nicht stillschweigend.

Akzeptanzkriterien:
- DB wird erzeugt.
- Tabellen existieren.
- Default-Mockdaten sind vorhanden.
- Backup-Datei wird erzeugt.
- Startbefehle sind im README dokumentiert.
```

## 5. Prompt 3: Domain-Logik und Tests

```text
Implementiere Arbeitspaket 3: zentrale Domain-Logik und Tests.

Aufgabe:
Implementiere reine, testbare Python-Funktionen für:
- Schaltjahrprüfung
- Stunden je Kalenderjahr: 8.760 bzw. 8.784
- MWh-zu-MW-Umrechnung
- Rundung: Preise 2 Nachkommastellen, MWh 0, MW 2
- Positionslimit: 1,00 MW je Kalenderjahr, Prüfung auf Absolutwert
- Vorzeicheninterpretation:
  - positive Menge = Partner kauft von uns
  - negative Menge = Partner verkauft an uns
- Validierung Limitorder:
  - Partner kauft erfordert positive Mengen
  - Partner verkauft erfordert negative Mengen
- Validierung Handelskalender:
  - Partner kauft erfordert positive Mengen
  - Partner verkauft erfordert negative Mengen
- Fälligkeit Handelskalender:
  - fällig, wenn Datum heute oder Vergangenheit und Status nicht erledigt
- Limitorder-Triggerprüfung für alle vier Bedingungen:
  - Partner kauft, wenn Preis > Limit
  - Partner kauft, wenn Preis < Limit
  - Partner verkauft, wenn Preis > Limit
  - Partner verkauft, wenn Preis < Limit

Wichtig:
- Implementiere Tests mit pytest.
- Tests sollen nicht von einem fixen echten Kalenderjahr abhängen. Aktuelles Jahr soll in Funktionen parametrisierbar sein, wenn nötig.

Akzeptanzkriterien:
- `pytest` läuft erfolgreich.
- Fachlogik ist ohne Streamlit testbar.
```

## 6. Prompt 4: Position-Seite

```text
Implementiere Arbeitspaket 4: Position-Service und Position-Seite.

Fachliche Regeln:
- Die App bestimmt das aktuelle Jahr automatisch.
- Positionen werden für Y0 bis Y+4 angezeigt.
- Mengen werden in MWh gespeichert.
- MW werden berechnet.
- Limit je Jahr = 1,00 MW.
- Limitprüfung auf Absolutwert.
- Die Position besteht aus:
  - PMS-Position aus portfolio_positions
  - Nettoeffekt untertägiger Geschäfte
  - simulierte Position = PMS-Position + untertägige Geschäfte
- In der Position-Seite keine Begriffe Kauf/Verkauf verwenden.
- Richtung ergibt sich nur aus dem Vorzeichen.

UI:
- Tabelle je Kalenderjahr mit:
  - Kalenderjahr
  - PMS-Position MW
  - untertägige Geschäfte MW
  - simulierte Position MW
  - Limit MW
  - Auslastung %
  - Status / Hervorhebung
- Darunter Tabelle der untertägigen Geschäfte.
- Formular zum Einfügen eines untertägigen Geschäfts:
  - Datum
  - Partner-Alias
  - Mengen in MWh für Y0 bis Y+4
- Kein Richtungsfeld.
- Button zum Löschen eines untertägigen Geschäfts.
- Nach Einfügen oder Löschen aktualisiert sich die Position.

Akzeptanzkriterien:
- Positionen werden korrekt berechnet.
- Limitverletzungen werden hervorgehoben.
- Untertägige Geschäfte können gespeichert und gelöscht werden.
- MW-Rundung auf 2 Nachkommastellen.
- MWh-Rundung auf 0 Nachkommastellen.
```

## 7. Prompt 5: Preise-Seite und Textgenerierung

```text
Implementiere Arbeitspaket 5: Preise-Service und Preise-Seite.

Produkte:
- Base Y+1
- Base Y+2
- Base Y+3
- Peak Y+1
- Peak Y+2
- Peak Y+3

Tabellenreihenfolge in der UI:
1. Base Y+1
2. Base Y+2
3. Base Y+3
4. Peak Y+1
5. Peak Y+2
6. Peak Y+3

Chattext-Reihenfolge:
1. Base Y+1
2. Peak Y+1
3. Base Y+2
4. Peak Y+2
5. Base Y+3
6. Peak Y+3

Aufgabe:
- Marktpreise aus DB laden und bearbeitbar anzeigen.
- OTC-Aufschläge aus DB laden und bearbeitbar anzeigen.
- Marktpreise und Aufschläge gemeinsam speichern.
- Finaler Preis = Marktpreis + OTC-Aufschlag.
- Settlementpreise aus DB anzeigen.
- Differenz = finaler Preis - Settlementpreis.
- Preise auf 2 Nachkommastellen runden.
- Chat-Kurztext erzeugen: nur finale Preise, keine Differenz.
- Mailtext erzeugen: finale Preise und Differenz zu Settlement Vortag.
- Keine echte E-Mail senden.
- PFC-Prüfung anzeigen:
  - PFC-Mittelwert
  - Settlementpreis
  - Zeitstempel PFC-Datei
  - Zeitstempel Settlementpreis

Akzeptanzkriterien:
- Alle sechs Produkte werden angezeigt.
- Speichern aktualisiert Marktpreise und Aufschläge gemeinsam.
- Chattext ist kopierbar.
- Mailtext ist kopierbar.
- PFC-Prüfung ist sichtbar.
```

## 8. Prompt 6: Excel- und PFC-Mockdatenimport

```text
Implementiere Arbeitspaket Excel-Mockdatenimport gemäß `06_excel_mockdaten_import.md`.

Ziel:
Ein Seed-Skript liest eine vorbereitete Excel-Mockdatei und optionale PFC-Dateien und befüllt daraus SQLite.

Befehl:
python scripts/seed_from_excel.py --excel data/mockdaten.xlsm --db data/app.db --pfc-dir data/pfc

Importquellen:
- Position aus Portfoliomanagementsystem: `Position Frontjahre!A7:H8`
- Untertägige Geschäfte: `Position Frontjahre!A9:H10`
- Preise und Aufschläge Base: `Vertriebsinfos!B14:C17`
- Preise und Aufschläge Peak: `Vertriebsinfos!G14:H17`
- Settlementpreise Base: `Vertriebsinfos!L14:L16`
- Handelskalender: `Handelskalender!A3:M6`
- Limitorder: `Limitorder!A5:G6`
- PFC-Dateien: `YYYYMMDD_EEX_PFC_YYYY.xlsx`, Mittelwert in `D2`

Regeln:
- Excel `K` bei Position/untertägigen Geschäften = negative Menge.
- Excel `V` bei Position/untertägigen Geschäften = positive Menge.
- Handelskalender `Kauf` = Partner kauft von uns = positive Menge.
- Handelskalender `Verkauf` = Partner verkauft an uns = negative Menge.
- Limitorder-Mockdaten enthalten nur `Partner kauft von uns, wenn Preis <= Limit`.
- Leeres Datum bei untertägigen Geschäften = heutiges Datum.
- Fehlende Peak-Settlementpreise als Default-Mockdaten erzeugen und im Importprotokoll kennzeichnen.
- Fehlende PFC-Dateien als Default-Mockdaten erzeugen und im Importprotokoll kennzeichnen.
- Bestehende DB nicht stillschweigend überschreiben.
- Nach erfolgreichem Seed `app_initial_backup.db` erzeugen.

Akzeptanzkriterien:
- Alle genannten Bereiche werden gelesen oder durch klare Defaults ersetzt.
- Importprotokoll zeigt, welche Werte aus Excel/PFC kamen und welche Defaults sind.
- App zeigt importierte Daten korrekt an.
```

## 9. Prompt 7: Limitorder-Seite

```text
Implementiere Arbeitspaket 6: Limitorder-Service und Limitorder-Seite.

Felder:
- Kunden-/Partner-Alias
- Liefermengen in MWh für Y0 bis Y+4
- Trigger-Preis:
  - Base Y+1
  - Base Y+2
  - Base Y+3
  - Peak Y+1
  - Peak Y+2
  - Peak Y+3
- Triggerbedingung:
  - Partner kauft, wenn Preis > Limit
  - Partner kauft, wenn Preis < Limit
  - Partner verkauft, wenn Preis > Limit
  - Partner verkauft, wenn Preis < Limit
- Limitpreis
- Verantwortlicher Handel
- Verantwortlicher Vertrieb
- optional gültig bis
- Status: offen, ausgeführt, gelöscht, abgelaufen

Regeln:
- Partner kauft erfordert positive Menge.
- Partner verkauft erfordert negative Menge.
- Limitorder wird gegen aktuellen Marktpreis des gewählten Trigger-Preises geprüft.
- Ausgelöste Limitorders werden hervorgehoben.
- Keine automatische Ausführung nur wegen Preisberührung.
- Button „Ausgeführt“ erzeugt ein untertägiges Geschäft mit heutigem Datum und setzt Status auf ausgeführt.
- Button „Gelöscht“ setzt Status auf gelöscht.

Akzeptanzkriterien:
- Neue Limitorder kann gespeichert werden.
- Vorzeichenvalidierung verhindert falsche Eingabe.
- Triggerprüfung funktioniert.
- Ausgeführte Order erzeugt genau ein untertägiges Geschäft.
- Gelöschte/ausgeführte Orders verschwinden aus der Standard-Offen-Ansicht oder werden deutlich anders dargestellt.
```

## 10. Prompt 8: Handelskalender-Seite

```text
Implementiere Arbeitspaket 7: Handelskalender-Service und Handelskalender-Seite.

Felder:
- Datum
- Partner-Alias
- Richtung:
  - Partner kauft
  - Partner verkauft
- Mengen in MWh für Y0 bis Y+4
- Status: geplant, fällig, erledigt

Anzeige:
- Zeige Einträge ab heute.
- Zeige zusätzlich überfällige, nicht erledigte Einträge.
- Erledigte Einträge werden in der Standardansicht nicht angezeigt.
- Fällig, wenn Datum heute oder Vergangenheit und Status nicht erledigt.

Regeln:
- Partner kauft erfordert positive Mengen.
- Partner verkauft erfordert negative Mengen.
- Button „Erledigt“ erzeugt ein untertägiges Geschäft.
- Danach Status auf erledigt setzen.
- Position aktualisiert sich danach.

Akzeptanzkriterien:
- Neue Einträge können gespeichert werden.
- Fällige/überfällige Einträge werden hervorgehoben.
- Erledigen erzeugt genau ein untertägiges Geschäft.
- Vorzeichenvalidierung funktioniert.
```

## 11. Prompt 9: Abschluss, Tests und Dokumentation

```text
Führe einen Abschlussdurchgang durch.

Aufgabe:
- Prüfe alle vier Streamlit-Seiten.
- Prüfe DB-Initialisierung.
- Prüfe Default-Mockdaten.
- Prüfe Excel-/PFC-Import, falls Testdateien vorhanden sind.
- Führe `pytest` aus.
- Prüfe, ob README alle Startbefehle enthält.
- Prüfe, ob keine Handelsentscheidung automatisch ausgeführt wird.
- Prüfe, ob kein Reset-Button in der UI existiert.
- Prüfe, ob Kauf/Verkauf-Begriffe in der Position-Seite vermieden werden.

Erstelle danach eine kurze Implementierungszusammenfassung mit:
- umgesetzte Funktionen
- bekannte Einschränkungen
- Startbefehle
- Testbefehle
- offene fachliche Fragen
```

## 12. Prompt für Bugfix nach Codex Review

```text
Codex hat folgenden Review-Kommentar geliefert:

[Hier Review-Kommentar einfügen]

Bitte:
1. Bewerte, ob der Kommentar zutrifft.
2. Behebe den Punkt minimal-invasiv.
3. Ändere nur die notwendigen Dateien.
4. Führe passende Tests aus.
5. Erkläre kurz, was geändert wurde.
6. Wenn der Review-Kommentar fachlich unklar ist, markiere ihn als Klärpunkt statt zu raten.
```
