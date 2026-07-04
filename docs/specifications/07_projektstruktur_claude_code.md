# Projektstruktur für Claude Code

## 1. Zweck dieses Dokuments

Dieses Dokument beschreibt die empfohlene Zielstruktur des Python-/Streamlit-/SQLite-Prototyps.

Wichtig: Die finale Projektstruktur soll durch **Claude Code** im Zielrepository angelegt werden. Dieses Dokument ist daher keine bereits angelegte Codebasis, sondern eine Arbeitsvorgabe und Orientierung.

Der Agent darf die Struktur pragmatisch anpassen, wenn dies die Umsetzung einfacher und robuster macht. Die fachliche Schichtung muss aber erhalten bleiben:

```text
Streamlit UI
  ↓
Services
  ↓
Repositories
  ↓
SQLAlchemy / SQLite

Domain-Logik bleibt unabhängig von Streamlit testbar.
```

## 2. Grundprinzipien

| Prinzip | Bedeutung |
|---|---|
| Einfacher Prototyp | Keine Enterprise-Architektur, keine unnötige Komplexität |
| Python-first | Fachlogik in Python, UI in Streamlit |
| SQLite als Mock-Datenschicht | Daten kommen im Prototyp aus SQLite, nicht direkt aus Excel zur Laufzeit |
| SQLAlchemy verwenden | Späterer Wechsel auf PostgreSQL soll nicht blockiert werden |
| Fachlogik testbar halten | Kernregeln nicht direkt in Streamlit-Seiten verstecken |
| Keine Vollautomatisierung | Die App unterstützt Entscheidungen, führt aber keine Handelsentscheidungen automatisch aus |
| Persistenz einfach halten | Daten bleiben in SQLite gespeichert, keine Historisierung, kein Reset-Button |
| Initiales Backup | Nach Seed wird `app_initial_backup.db` erzeugt |

## 3. Empfohlene Zielstruktur

Claude Code soll die Struktur im Zielprojekt anlegen, z. B. so:

```text
energy_trading_prototype/
  README.md
  requirements.txt
  pyproject.toml                 # optional, wenn Claude Code es sinnvoll nutzt
  app.py

  pages/
    1_Position.py
    2_Preise.py
    3_Limitorder.py
    4_Handelskalender.py

  scripts/
    init_db.py
    seed_from_excel.py
    seed_default_mock_data.py

  src/
    __init__.py
    config.py

    db/
      __init__.py
      database.py
      models.py
      init_db.py

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
      metadata_repository.py

    services/
      __init__.py
      initialization_service.py
      position_service.py
      price_service.py
      limit_order_service.py
      trading_calendar_service.py
      excel_import_service.py
      pfc_import_service.py

  data/
    app.db                       # wird erzeugt, nicht manuell pflegen
    app_initial_backup.db         # wird nach Initial-Seed erzeugt
    mockdaten.xlsm                # vorbereitete Excel-Mockdatei, falls vorhanden
    pfc/
      20260702_EEX_PFC_2027.xlsx
      20260702_EEX_PFC_2028.xlsx
      20260702_EEX_PFC_2029.xlsx

  tests/
    test_quantity_utils.py
    test_position_logic.py
    test_price_logic.py
    test_limit_order_logic.py
    test_trading_calendar_logic.py
    test_excel_import_mapping.py
```

## 4. Minimal zulässige Abweichungen

Claude Code darf diese Anpassungen vornehmen:

| Bereich | Erlaubte Anpassung |
|---|---|
| Paketverwaltung | `requirements.txt` allein ist ausreichend; `pyproject.toml` optional |
| Repository-Dateien | mehrere kleine Repositories oder ein gemeinsames Repository-Modul sind okay |
| Tests | Tests dürfen zunächst auf Domain-Logik fokussieren |
| Scripts | Initialisierung kann in `scripts/` oder in `src/services/` liegen, solange Aufruf klar dokumentiert ist |
| Streamlit-Seiten | Dateinamen dürfen leicht angepasst werden, wenn Navigation sauber bleibt |

Nicht erlaubt:

```text
- gesamte Fachlogik direkt in app.py schreiben
- Streamlit-Seiten direkt SQLAlchemy-Queries zusammenbauen lassen
- Kauf/Verkauf aus eigener Perspektive uneindeutig verwenden
- Limitorders automatisch ausführen, nur weil ein Preis erreicht ist
- bestehende Datenbank ohne Warnung überschreiben
- Reset-Button in der UI einbauen
```

## 5. Laufbefehle für den Prototyp

Claude Code soll im `README.md` des Zielprojekts konkrete Befehle dokumentieren.

Empfohlener Minimalablauf:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/init_db.py
python scripts/seed_default_mock_data.py
streamlit run app.py
```

Für den Excel-Mockdatenimport:

```bash
python scripts/seed_from_excel.py --excel data/mockdaten.xlsm --db data/app.db --pfc-dir data/pfc
```

Falls die Excel-Datei oder PFC-Dateien fehlen, darf das Seed-Skript realistische Default-Mockdaten erzeugen. Das muss klar in der Konsolenausgabe und optional in einer Importzusammenfassung sichtbar sein.

## 6. Verantwortlichkeiten der Schichten

### 6.1 Streamlit-Seiten

Streamlit-Seiten zeigen Daten an, nehmen Eingaben entgegen und rufen Services auf.

Sie enthalten nur wenig Logik:

```text
- Formulare
- Tabellenanzeige
- Buttons
- einfache Hervorhebung
- Ausgabe von Chat-/Mailtexten
```

### 6.2 Services

Services koordinieren fachliche Abläufe:

```text
- Position berechnen
- Preise speichern und final berechnen
- Limitorder prüfen und auf ausgeführt setzen
- Handelskalendereintrag erledigen und untertägiges Geschäft erzeugen
- Excel-Mockdaten importieren
```

### 6.3 Domain

Domain-Module enthalten reine Fachlogik:

```text
- Schaltjahrlogik
- MWh/MW-Umrechnung
- Limitprüfung
- Vorzeicheninterpretation
- Triggerprüfung für Limitorders
- Fälligkeitslogik Handelskalender
- Textgenerierung für Chat/Mail
```

Diese Funktionen sollen ohne Streamlit und ohne Datenbank testbar sein.

### 6.4 Repositories

Repositories kapseln Datenbankzugriffe:

```text
- laden
- speichern
- aktualisieren
- Status setzen
- einfache Filter
```

### 6.5 Datenbankmodelle

SQLAlchemy-Modelle bilden die Tabellen aus `02_datenmodell_sqlite.md` ab.

## 7. Wichtige fachliche Konstanten

Claude Code soll zentrale Konstanten definieren, z. B. in `src/config.py` oder einem Domain-Modul:

```python
POSITION_LIMIT_MW = 1.0
PRICE_PRODUCT_ORDER_TABLE = [
    ("Base", "Y+1"),
    ("Base", "Y+2"),
    ("Base", "Y+3"),
    ("Peak", "Y+1"),
    ("Peak", "Y+2"),
    ("Peak", "Y+3"),
]
PRICE_PRODUCT_ORDER_TEXT = [
    ("Base", "Y+1"),
    ("Peak", "Y+1"),
    ("Base", "Y+2"),
    ("Peak", "Y+2"),
    ("Base", "Y+3"),
    ("Peak", "Y+3"),
]
```

Die Jahreswerte sind nicht hart zu codieren, sondern aus dem aktuellen Jahr abzuleiten.

Für Tests soll die aktuelle Jahreslogik injizierbar oder parametrisierbar sein, damit Tests nicht je nach Kalenderjahr brechen.

## 8. Rundungsregeln

| Werttyp | Rundung |
|---|---:|
| Preise in EUR/MWh | 2 Nachkommastellen |
| Mengen in MWh | 0 Nachkommastellen |
| Mengen in MW | 2 Nachkommastellen |

## 9. Sicherheitsrelevante UI-Regeln

Die App soll klare Begriffe verwenden:

| Fall | UI-Text |
|---|---|
| Positive Menge | Partner kauft von uns |
| Negative Menge | Partner verkauft an uns |

In der Position-Seite soll ganz auf „Kauf“ und „Verkauf“ verzichtet werden. Dort ist nur das Vorzeichen bzw. die Positionswirkung sichtbar.

Limitorder und Handelskalender dürfen „Partner kauft“ / „Partner verkauft“ verwenden, müssen aber die Vorzeichenvalidierung erzwingen.

## 10. Reihenfolge der Umsetzung

Empfohlene Reihenfolge für Claude Code:

1. Projektstruktur und leere App
2. SQLAlchemy-Modelle und DB-Initialisierung
3. Default-Mockdaten
4. zentrale Domain-Logik und Tests
5. Position-Seite
6. Preise-Seite
7. Excel-/PFC-Mockdatenimport
8. Limitorder-Seite
9. Handelskalender-Seite
10. End-to-End-Polish und Codex Review

Die Reihenfolge kann leicht angepasst werden, aber Position und Datenmodell sollten früh stehen.
