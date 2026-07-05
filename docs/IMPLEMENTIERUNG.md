# Implementierungszusammenfassung (Abschluss AP9)

Stand des Prototyps nach Abschluss der Arbeitspakete 1-9. Grundlage:
`docs/specifications/05_umsetzungsplan_codex_claude.md` und
`08_claude_code_prompts.md`.

## Umgesetzte Funktionen

- **Vier Streamlit-Seiten** (ohne separate Fachstartseite):
  - **Position** – PMS-Position, untertägige Geschäfte und simulierte Position
    je Kalenderjahr (Y0–Y+4), Limit 1,00 MW auf Absolutwert, Auslastung und
    Hervorhebung bei Überschreitung. Einfügen/Löschen untertägiger Geschäfte.
    Keine Kauf/Verkauf-Richtungsfelder – Richtung nur über das Vorzeichen.
  - **Preise / Vertriebsinfos** – Marktpreise und OTC-Aufschläge gemeinsam
    pflegen, finaler Preis und Settlement-Differenz, kopierbarer Chat- und
    Mailtext, PFC-Prüfung (Mittelwert + Zeitstempel).
  - **Limitorder** – Anlegen mit Vorzeichenvalidierung, Triggerprüfung gegen
    den Marktpreis (nur Hervorhebung), Buttons „Ausgeführt“/„Gelöscht“.
  - **Handelskalender** – fällige/überfällige Einträge hervorgehoben,
    „Erledigt“ erzeugt ein untertägiges Geschäft.
- **Datenhaltung**: SQLite über SQLAlchemy, 9 Fachtabellen, DB-Initialisierung,
  Default-Mockdaten und initiales Backup nach dem Seed.
- **Excel-/PFC-Import**: Seed aus `data/mockdaten.xlsm` und `data/pfc/`;
  fehlende Werte werden als klar gekennzeichnete Default-Mockdaten erzeugt.
  Eine bereits befüllte DB wird nicht stillschweigend überschrieben.
- **Domain-Logik** (`src/domain`) ist vollständig ohne Streamlit/DB testbar
  (Schaltjahr, MWh/MW, Limit, Vorzeichen, Limitorder-Trigger, Fälligkeit).
- **Deutsche Zahlenanzeige** in allen Tabellen und Listen (1.234,56).

## Abnahme-Ergebnisse (AP9)

- Alle vier Seiten + `app.py` rendern headless fehlerfrei (Streamlit `AppTest`).
- End-to-End-Seed gegen die echten Excel-/PFC-Dateien füllt alle Tabellen;
  erneuter Import wird korrekt als „bereits initialisiert“ abgewiesen.
- `pytest`: 110 Tests grün; `src/domain` zu 100 % abgedeckt.
- Keine automatische Handelsausführung: untertägige Geschäfte entstehen nur
  über Formular-Submit bzw. die Buttons „Ausgeführt“/„Erledigt“.
- Kein Reset-Button in der UI. Auf der Position-Seite keine Kauf/Verkauf-
  Richtungselemente (nur ein erklärender Hinweistext zur Vorzeichenlogik).

## Bekannte Einschränkungen

- Reiner **Prototyp mit Mockdaten**; SQLite als Mock-Datenschicht.
- **Eingabefelder** (`st.number_input`) zeigen den Dezimaltrenner technisch
  bedingt weiterhin als Punkt; die deutsche Formatierung betrifft nur die
  Anzeige (Tabellen/Listen/Texte).
- `scripts/seed_from_excel.py --db` wird ignoriert – es wird immer die in
  `src/config.py` konfigurierte Datenbank verwendet.
- Zeitstempel werden als naives UTC gespeichert.
- Beim Lesen der `.xlsx`-Dateien meldet openpyxl harmlose `UserWarning`s
  (fehlender Default-Style) – kein Fehler im Projektcode.

## Startbefehle

```bash
# Installation
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# DB initialisieren + Default-Mockdaten
python scripts/init_db.py
python scripts/seed_default_mock_data.py

# alternativ: Seed aus Excel-/PFC-Mockdaten
python scripts/seed_from_excel.py --excel data/mockdaten.xlsm --db data/app.db --pfc-dir data/pfc

# App starten
streamlit run app.py          # oder: .\start_app.ps1
```

## Testbefehle

```bash
pytest
coverage run --source=src -m pytest && coverage report -m
```

## Offene fachliche Fragen

- Herkunft der **Peak-Settlementpreise**: aktuell Default-Mockwerte, da nicht in
  der Excel-Mockdatei enthalten – bei Produktivnutzung zu klären.
- **Verantwortliche (Handel/Vertrieb)** für importierte Limitorders fehlen in
  der Mockdatei und werden mit Platzhaltern befüllt.
- Migrationspfad **SQLite → PostgreSQL** ist vorbereitet (SQLAlchemy), aber
  noch nicht ausgeführt.
