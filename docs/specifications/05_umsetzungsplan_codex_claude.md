# Umsetzungsplan für Codex oder Claude Code

## 1. Ziel dieses Dokuments

Dieses Dokument beschreibt die empfohlene technische Umsetzung des Prototyps in Arbeitspaketen für einen Coding-Agenten wie Codex oder Claude Code.

Der Coding-Agent soll nicht versuchen, die Excel-Datei 1:1 nachzubauen. Stattdessen soll er die fachlichen Funktionen in eine saubere Python-/Streamlit-/SQLite-Anwendung übersetzen.

## 2. Ziel-Stack

- Python 3.12 oder neuer
- Streamlit
- SQLite
- SQLAlchemy
- pandas
- pytest optional

## 3. Empfohlene Projektstruktur

```text
energy_trading_prototype/
  README.md
  requirements.txt
  pyproject.toml
  app.py

  pages/
    1_Position.py
    2_Preise.py
    3_Limitorder.py
    4_Handelskalender.py

  src/
    config.py

    db/
      __init__.py
      database.py
      models.py
      init_db.py
      seed_mock_data.py

    domain/
      __init__.py
      calendar_utils.py
      quantity_utils.py
      position_logic.py
      price_logic.py
      limit_order_logic.py
      trading_calendar_logic.py
      text_generation.py
      validation.py

    repositories/
      __init__.py
      portfolio_repository.py
      intraday_trade_repository.py
      price_repository.py
      limit_order_repository.py
      trading_calendar_repository.py

    services/
      __init__.py
      position_service.py
      price_service.py
      limit_order_service.py
      trading_calendar_service.py
      initialization_service.py

  data/
    app.db
    app_initial_backup.db

  tests/
    test_quantity_utils.py
    test_position_logic.py
    test_limit_order_logic.py
    test_trading_calendar_logic.py
```

## 4. Architekturprinzip

Streamlit soll nur UI-Schicht sein.

Fachlogik gehört nicht direkt in die Streamlit-Seiten, sondern in `src/domain` und `src/services`.

```text
Streamlit-Seite
  ↓
Service
  ↓
Repository
  ↓
SQLAlchemy / SQLite
```

## 5. Arbeitspaket 1: Projektgrundlage erstellen

### Ziel

Eine lauffähige leere Streamlit-App mit Grundstruktur erzeugen.

### Aufgaben

- Projektordner anlegen
- `requirements.txt` oder `pyproject.toml` erstellen
- Streamlit installieren
- SQLAlchemy installieren
- `app.py` mit Navigation oder Infotext anlegen
- `pages/` mit vier Seiten anlegen
- `src/`-Struktur anlegen

### Akzeptanzkriterien

- `streamlit run app.py` startet fehlerfrei
- vier Seiten sind sichtbar
- noch keine Fachlogik erforderlich

## 6. Arbeitspaket 2: Datenbankmodell und Initialisierung

### Ziel

SQLite-Datenbank mit SQLAlchemy-Modellen erzeugen.

### Aufgaben

- SQLAlchemy Engine und Session einrichten
- Modelle für folgende Tabellen anlegen:
  - `portfolio_positions`
  - `intraday_trades`
  - `market_prices`
  - `otc_surcharges`
  - `settlement_prices`
  - `pfc_checks`
  - `limit_orders`
  - `trading_calendar`
  - `app_metadata`
- Initialisierung implementieren
- Mock-Daten einfügen
- initiales Backup erzeugen

### Akzeptanzkriterien

- `data/app.db` wird erzeugt
- Tabellen existieren
- Mock-Daten sind vorhanden
- `data/app_initial_backup.db` wird erzeugt

## 7. Arbeitspaket 3: Hilfsfunktionen und Validierung

### Ziel

Zentrale fachliche Hilfsfunktionen implementieren.

### Aufgaben

Implementiere:

- `is_leap_year(year)`
- `hours_in_year(year)`
- `mwh_to_mw(quantity_mwh, year)`
- Rundungsfunktionen
- Vorzeicheninterpretation
- Validierung für Mengen
- Validierung für Limitorder-Vorzeichen
- Validierung für Handelskalender-Vorzeichen

### Akzeptanzkriterien

- Schaltjahre werden korrekt erkannt
- 8.760/8.784 Stunden werden korrekt verwendet
- positive Menge wird als „Partner kauft von uns“ interpretiert
- negative Menge wird als „Partner verkauft an uns“ interpretiert
- Limitorder- und Kalender-Validierungen verhindern widersprüchliche Eingaben

## 8. Arbeitspaket 4: Position-Service und Position-Seite

### Ziel

Position je Kalenderjahr anzeigen und untertägige Geschäfte erfassen.

### Aufgaben

- PMS-Mock-Positionen aus DB lesen
- untertägige Geschäfte aus DB lesen
- Position je Jahr berechnen
- Limitprüfung durchführen
- Position-Seite bauen
- Formular für untertägige Geschäfte bauen
- Löschen-Funktion für untertägige Geschäfte bauen

### Akzeptanzkriterien

- Position je Jahr Y0 bis Y+4 wird angezeigt
- PMS-Position und untertägige Position werden separat angezeigt
- simulierte Position wird berechnet
- Limitverletzungen werden hervorgehoben
- untertägiges Geschäft kann eingefügt werden
- Position aktualisiert sich danach
- untertägiges Geschäft kann gelöscht werden

## 9. Arbeitspaket 5: Preise-Service und Preise-Seite

### Ziel

Marktpreise, OTC-Aufschläge, Settlement-Vergleich und Textgenerierung umsetzen.

### Aufgaben

- Preise aus DB lesen und speichern
- OTC-Aufschläge aus DB lesen und speichern
- Settlementpreise aus DB lesen
- finale Preise berechnen
- Differenzen berechnen
- Preise-Seite bauen
- Chattext erzeugen
- Mailtext erzeugen
- PFC-Prüfung anzeigen

### Akzeptanzkriterien

- sechs Preisprodukte werden angezeigt
- Marktpreise und Aufschläge können gemeinsam gespeichert werden
- finaler Preis wird berechnet
- Settlement-Differenz wird angezeigt
- Chattext enthält finale Preise in korrekter Reihenfolge
- Mailtext enthält finale Preise und Settlement-Differenzen
- PFC-Prüfung zeigt Mittelwerte und Zeitstempel

## 10. Arbeitspaket 6: Limitorder-Service und Limitorder-Seite

### Ziel

Limitorders erfassen, prüfen und ausführen.

### Aufgaben

- Limitorder-Modell nutzen
- Formular für neue Limitorder bauen
- Trigger-Preis auswählen
- Auslöseart auswählen
- Vorzeichen validieren
- aktuelle Marktpreise lesen
- Limitorders gegen Marktpreise prüfen
- ausgelöste Orders hervorheben
- Button „Ausgeführt“ implementieren
- Button „Gelöscht“ implementieren
- bei „Ausgeführt“ untertägiges Geschäft erzeugen

### Akzeptanzkriterien

- Limitorder kann gespeichert werden
- Partner-kauft-Orders erzwingen positive Mengen
- Partner-verkauft-Orders erzwingen negative Mengen
- Limitorder wird gegen Trigger-Preis geprüft
- ausgelöste Order wird hervorgehoben
- Klick auf „Ausgeführt“ erzeugt untertägiges Geschäft
- Limitorder erhält Status `ausgeführt`
- Klick auf „Gelöscht“ setzt Status `gelöscht`

## 11. Arbeitspaket 7: Handelskalender-Service und Handelskalender-Seite

### Ziel

Handelskalendereinträge erfassen, fällige Einträge anzeigen und erledigen.

### Aufgaben

- Formular für Handelskalendereintrag bauen
- Richtung Partner kauft/verkauft erfassen
- Vorzeichen validieren
- Einträge speichern
- Anzeige filtern:
  - ab heute
  - plus überfällige, nicht erledigte Einträge
- Fälligkeit berechnen
- fällige Einträge hervorheben
- Button „Erledigt“ implementieren
- bei „Erledigt“ untertägiges Geschäft erzeugen

### Akzeptanzkriterien

- Eintrag kann gespeichert werden
- Vorzeichenlogik wird erzwungen
- fällige/überfällige Einträge werden hervorgehoben
- erledigte Einträge verschwinden aus Standardansicht
- Klick auf „Erledigt“ erzeugt untertägiges Geschäft
- Position wird danach aktualisiert

## 12. Arbeitspaket 8: Tests und technische Qualität

### Ziel

Die wichtigsten Fachregeln mit einfachen Tests absichern.

### Aufgaben

Tests für:

- Schaltjahrlogik
- MWh/MW-Umrechnung
- Limitprüfung
- Vorzeicheninterpretation
- Limitorder-Auslösung
- Handelskalender-Fälligkeit

### Akzeptanzkriterien

- `pytest` läuft erfolgreich
- Kernlogik ist unabhängig von Streamlit testbar

## 13. Coding-Agent-Prompt: Gesamtauftrag

```text
Du bist ein Coding-Agent. Baue einen Prototypen einer internen Energiehandels-Anwendung mit Python, Streamlit, SQLite und SQLAlchemy.

Wichtig:
- Baue keine produktive Enterprise-App.
- Baue eine einfache, fachlich nachvollziehbare Streamlit-App.
- Verwende SQLite als Mock-Datenschicht.
- Verwende SQLAlchemy, damit später ein Wechsel auf PostgreSQL möglich ist.
- Trenne UI, Services, Repositories und Fachlogik.
- Implementiere vier Seiten: Position, Preise, Limitorder, Handelskalender.
- Automatisiere keine Handelsentscheidungen. Die App darf nur berechnen, anzeigen, hervorheben und untertägige Geschäfte aus aktiv erledigten Limitorders/Kalendereinträgen erzeugen.

Setze die Spezifikation aus den Markdown-Dateien um.
```

## 14. Coding-Agent-Prompt: Erstes Arbeitspaket

```text
Erstelle die Projektstruktur für eine Streamlit-App mit Python und SQLAlchemy.

Lege an:
- app.py
- pages/1_Position.py
- pages/2_Preise.py
- pages/3_Limitorder.py
- pages/4_Handelskalender.py
- src/db/database.py
- src/db/models.py
- src/db/init_db.py
- src/db/seed_mock_data.py
- src/domain/quantity_utils.py
- src/domain/position_logic.py
- src/domain/price_logic.py
- src/domain/limit_order_logic.py
- src/domain/trading_calendar_logic.py
- src/domain/validation.py
- src/repositories/
- src/services/

Implementiere zunächst nur:
- Datenbankverbindung
- SQLAlchemy-Modelle
- DB-Initialisierung
- einfache Mock-Daten
- leere Streamlit-Seiten mit Überschrift

Achte auf saubere, verständliche Struktur.
```

## 15. Coding-Agent-Prompt: Position zuerst implementieren

```text
Implementiere zuerst die Seite Position.

Fachregeln:
- aktuelles Jahr automatisch bestimmen
- Jahre Y0 bis Y+4 anzeigen
- Mengen werden in MWh gespeichert
- MW = MWh / Stunden des Jahres
- Schaltjahre haben 8.784 Stunden, andere Jahre 8.760
- Limit je Jahr: 1,00 MW
- Limitprüfung auf Absolutwert
- positive Menge = Partner kauft von uns = Position steigt
- negative Menge = Partner verkauft an uns = Position sinkt
- untertägige Geschäfte haben kein Richtungsfeld

UI:
- Tabelle Position je Kalenderjahr
- PMS-Position MW
- untertägige Geschäfte MW
- simulierte Position MW
- Limit MW
- Auslastung %
- Status
- darunter Tabelle untertägige Geschäfte
- Formular zum Einfügen
- Button zum Löschen
```


---

# Ergänzung: Arbeitspaket Excel-Mockdatenimport

Dieses Arbeitspaket basiert auf `06_excel_mockdaten_import.md`.

## Ziel

Ein Seed-Skript liest eine vorbereitete Excel-Mockdatei und befüllt daraus die SQLite-Datenbank.

## Technischer Zielbefehl

```bash
python scripts/seed_from_excel.py --excel data/mockdaten.xlsm --db data/app.db --pfc-dir data/pfc
```

## Umsetzungsaufgaben

1. Excel-Datei öffnen.
2. Zellbereiche gemäß `06_excel_mockdaten_import.md` lesen.
3. Daten in Python-Zwischenstrukturen normalisieren.
4. Alte Excel-Richtungen `K`/`V` und Handelskalender-Richtungen `Kauf`/`Verkauf` in die neue Vorzeichenlogik übersetzen. Dabei gilt: `Kauf` = Partner kauft von uns = positive Menge, `Verkauf` = Partner verkauft an uns = negative Menge.
5. SQLAlchemy-Modelle befüllen.
6. Initiales SQLite-Backup erzeugen.
7. Importvalidierungen und klare Fehlermeldungen implementieren.
8. Leere Datumsfelder bei untertägigen Geschäften mit dem heutigen Datum befüllen.
9. `Kauf-Limit` in den Mock-Daten als `Partner kauft, wenn Preis <= Limit` importieren.
10. Base-Settlementpreise aus `Vertriebsinfos!L14:L16` für Y+1 bis Y+3 importieren.
11. Fehlende Peak-Settlementpreise oder leere Base-Werte als realistische Default-Mockdaten erzeugen und im Importprotokoll kennzeichnen.
12. PFC-Dateien aus einem Verzeichnis, z. B. `data/pfc/`, lesen.
13. Dateimuster `YYYYMMDD_EEX_PFC_YYYY.xlsx` validieren.
14. PFC-Mittelwert je Datei aus `D2` lesen.
15. PFC-Generierungsdatum und Lieferjahr aus dem Dateinamen ableiten.
16. Fehlende PFC-Dateien oder fehlerhafte `D2`-Werte als Default-Mockdaten ersetzen und im Importprotokoll kennzeichnen.

## Akzeptanzkriterien

- Leere Datenbank wird aus Excel-Mockdaten befüllt.
- Bestehende Datenbank wird nicht stillschweigend überschrieben.
- `app_initial_backup.db` wird nach erfolgreichem Seed erzeugt.
- Position, Preise, untertägige Geschäfte, Handelskalender und Limitorders sind in der App sichtbar.
- Vorzeichenlogik wird konsistent eingehalten.
- Handelskalender-Import mappt `Kauf` sicher auf `Partner kauft von uns`.
- Limitorder-Import unterstützt den Mock-Fall `Partner kauft, wenn Preis <= Limit`.
- Leere Datumsfelder werden beim Import mit dem heutigen Datum gefüllt.


---

## 16. Aktualisierte Rollenverteilung

Für die weitere Umsetzung gilt:

```text
Claude Code = Implementierung
Codex       = Code Review
```

Die finale Projektstruktur soll von Claude Code im Zielrepository angelegt werden. Die Spezifikation beschreibt Zielstruktur, fachliche Regeln und Akzeptanzkriterien, legt aber nicht vorab physisch die Codebasis an.

Für die konkrete Arbeit sollen zusätzlich verwendet werden:

| Datei | Zweck |
|---|---|
| `07_projektstruktur_claude_code.md` | Zielstruktur, Schichten, technische Leitplanken |
| `08_claude_code_prompts.md` | konkrete Umsetzungs-Prompts für Claude Code |
| `09_codex_review_prompts.md` | konkrete Review-Prompts für Codex |
| `10_agent_workflow.md` | Ablauf Implementierung → Review → Fixes |
```

Empfohlener Ablauf:

```text
1. Claude Code liest alle Spezifikationsdateien.
2. Claude Code legt die Projektstruktur an.
3. Claude Code implementiert ein Arbeitspaket.
4. Codex reviewt das Arbeitspaket gegen die Spezifikation.
5. Claude Code behebt nur die notwendigen Review-Punkte.
6. Nächstes Arbeitspaket.
```
