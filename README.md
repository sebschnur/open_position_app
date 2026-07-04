# Energiehandels-Prototyp (Excel-Abloesung)

Prototyp zur Abloesung einer Excel-/VBA-Datei durch **Python + Streamlit + SQLite + SQLAlchemy**.

Die fachliche Spezifikation liegt unter [`docs/specifications/`](docs/specifications/).
Dieser Prototyp arbeitet ausschliesslich mit Mockdaten. SQLite ist die zentrale
Mock-Datenschicht; die Excel-Dateien dienen nur als initiale Mockdatenquelle.

> Status: **Projektgeruest angelegt.** Fachlogik ist noch nicht implementiert.
> Die Umsetzung erfolgt schrittweise gemaess den Arbeitspaketen in
> `docs/specifications/05_umsetzungsplan_codex_claude.md` und
> `docs/specifications/08_claude_code_prompts.md`.

## Architektur

```text
Streamlit UI (app.py, pages/)
  -> Services (src/services)
  -> Repositories (src/repositories)
  -> SQLAlchemy / SQLite (src/db)

Domain-Logik (src/domain) bleibt unabhaengig von Streamlit testbar.
```

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
```

## Datenbank initialisieren und befuellen

```bash
python scripts/init_db.py
python scripts/seed_default_mock_data.py
```

Optional: Initialbefuellung aus Excel-Mockdaten und PFC-Dateien

```bash
python scripts/seed_from_excel.py --excel data/mockdaten.xlsm --db data/app.db --pfc-dir data/pfc
```

## App starten

```bash
streamlit run app.py
```

## Tests

```bash
pytest
```

## Projektstruktur

Siehe `docs/specifications/07_projektstruktur_claude_code.md`.
