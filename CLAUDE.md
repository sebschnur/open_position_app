# Energiehandels-Prototyp — Projektkontext

Prototyp zur Abloesung einer Excel-/VBA-Loesung durch **Streamlit + SQLAlchemy +
SQLite**. Reiner Prototyp mit Mockdaten; SQLite ist die zentrale Datenschicht,
die Excel-/PFC-Dateien dienen nur als initiale Mockquelle.

Die **verbindliche Fachspezifikation** liegt in `docs/specifications/` (00–10) —
bei fachlichen Fragen zuerst dort nachlesen (v. a. `01_fachliche_funktionen.md`,
`02_datenmodell_sqlite.md`, `03_streamlit_ui_konzept.md`, `04_workflows_...`,
`06_excel_mockdaten_import.md`). Aktueller Umsetzungsstand: `docs/IMPLEMENTIERUNG.md`,
Aenderungshistorie: `docs/specifications/CHANGELOG.md`.

## Architektur & Schichten (strikt einhalten)

```
Streamlit UI (app.py, views/)
  -> Services      (src/services)      Orchestrierung, committen, Row-Dataclasses fuer die UI
  -> Repositories  (src/repositories)  DB-Zugriff je Tabelle, KEIN commit (Aufrufer entscheidet)
  -> Models/DB     (src/db)            SQLAlchemy-Modelle, Engine/Session, Init/Seed

Domain-Logik (src/domain): reine Funktionen, KEIN Streamlit/DB-Import, voll unit-testbar
```

- UI ruft **nur Services**, nie direkt Repositories oder Models.
- Services validieren, orchestrieren und `commit`en; Repositories `flush`en nur.
- Domain ist seiteneffektfrei (Jahre, MWh/MW, Vorzeichen, Trigger, Faelligkeit).

## Verzeichnisse

- `app.py` — **einziger Einstiegspunkt**: setzt ueber `apply_global_layout()`
  einmalig Wide-Layout + globales CSS und schaltet die Seiten via
  `st.navigation`/`st.Page`. Weil `app.py` bei jedem Seitenwechsel durchlaeuft,
  gelten Layout/CSS automatisch fuer alle Seiten — **keine Seite setzt das
  selbst** (kein `set_page_config`/`configure_wide_page` in `views/`; per Test
  `tests/test_layout_bootstrap.py` abgesichert).
- `views/` — je Fachseite ein eigenstaendiges Skript: `position.py`, `preise.py`,
  `limitorder.py`, `handelskalender.py`. Kein Zahlpraefix, kein magischer
  `pages/`-Ordner mehr (Reihenfolge/Titel kommen aus `st.Page` in `app.py`).
- `src/services/` — Anwendungslogik + `@dataclass`-Rows fuer die Anzeige.
- `src/repositories/` — ein Modul je Tabelle, nur DB-Zugriff.
- `src/domain/` — reine Fachlogik (`quantity_utils`, `position_logic`,
  `limit_order_logic`, `trading_calendar_logic`, `validation`, `calendar_utils`).
- `src/db/` — `models.py`, `database.py` (Engine/`SessionLocal`), `init_db.py`
  (`create_all` + leichte Migration), `seed_default_mock_data.py`.
- `src/user_context.py` — `get_current_username()` (Nachvollziehbarkeit).
- `src/format_utils.py` — `format_de(...)` (deutsche Zahlen).
- `tests/` — pytest, isolierte In-Memory-SQLite.
- `scripts/` — CLI: `init_db.py`, `seed_default_mock_data.py`, `seed_from_excel.py`.

## Projektkonventionen

- **Jahreslogik**: feste Spalten `quantity_y0_mwh` .. `quantity_y4_mwh`
  (Y0 = aktuelles Jahr). Aktuelles Jahr immer aus `today.year` ableiten, nie
  hart codieren. In der UI **konkrete Jahre** anzeigen (z. B. 2026…2030), nicht
  `Y0…Y4`.
- **Mengen** werden in MWh gespeichert; MW werden berechnet (`mwh_to_mw`,
  `hours_in_year`). Rundung nur fuer die Anzeige (Preise 2, MWh 0, MW 2).
- **Deutsche Zahlen** ueber `format_de(...)` bzw. pandas
  `Styler.format(thousands=".", decimal=",")` — **nicht** ueber `column_config`
  (nur englisches Format). `st.number_input` zeigt den Punkt technisch bedingt.
- **Zeitstempel**: naives UTC (`dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)`).
- **Nachvollziehbarkeit**: jeder manuelle Eintrag speichert
  `last_modified_by = get_current_username()`. Button-Aktionen
  (Ausgefuehrt/Geloescht/Erledigt) ersetzen den Wert — auch in erzeugten
  untertaegigen Geschaeften. Neue manuelle Tabellen ebenso ausstatten und in der
  UI als Spalte „Geaendert von" zeigen.
- **Keine automatische Handelsausfuehrung**: untertaegige Geschaefte entstehen
  nur per Formular-Submit oder Button.
- **Position-Seite**: keine „Kauf"/„Verkauf"-Begriffe — Richtung ergibt sich
  ausschliesslich aus dem Vorzeichen der Menge.
- **Schema-Aenderungen** an bestehenden Tabellen: `create_all()` zieht keine
  Spalten nach → Migration in `init_db._ensure_last_modified_by_columns` als
  Vorlage nutzen (`PRAGMA table_info` + `ALTER TABLE ADD COLUMN`).

## Tests

- `pytest`, isolierte In-Memory-DB je Test
  (`create_engine("sqlite:///:memory:")` + `Base.metadata.create_all`).
- `today` **und** `username` in Services injizieren, nicht auf Systemuhr/OS-User
  verlassen (Determinismus).
- Domain-Logik zu 100 % abgedeckt halten.

## Befehle

```bash
# Tests
python -m pytest -q
coverage run --source=src -m pytest && coverage report -m

# App starten (Windows nutzt .venv)
streamlit run app.py            # oder:  .\start_app.ps1

# DB initialisieren + befuellen
python scripts/init_db.py
python scripts/seed_default_mock_data.py
python scripts/seed_from_excel.py --excel data/mockdaten.xlsm --pfc-dir data/pfc
```

## Git

- Solo-Projekt, Commits liegen linear auf `main`. **Eigenes Repo**: Git-Wurzel ist
  dieser App-Ordner selbst (seit 2026-07-12 aus dem uebergeordneten `projects/`-Repo
  ausgelagert), Remote `origin` = GitHub `sebschnur/open_position_app`. Normales
  `git add -A` ist sicher; keine Teilbaum-Sonderregeln mehr.
- Vor Commits: Tests gruen und App bootet headless fehlerfrei.

## Qualitaets-Gate (pre-commit)

- Es gibt keine CI/CD - **pre-commit ist das Gate**. Setup: `pip install -r
  requirements-dev.txt` und `pre-commit install`.
- Hooks: Ruff (Lint+Format, line-length 88; `E501`/`UP038` bewusst ignoriert),
  **mypy** ueber `mirrors-mypy` (isolierte Umgebung, Config aus `[tool.mypy]` in
  `pyproject.toml`, prueft nur `src/`). Manuell: `pre-commit run --all-files`.
- mypy-Hinweis: die isolierte mypy-Umgebung hat die Projekt-Dependencies **nicht**
  installiert (`ignore_missing_imports = true` faengt das ab). Sollen DB-Typen echt
  geprueft werden, `additional_dependencies` im mypy-Hook ergaenzen.
