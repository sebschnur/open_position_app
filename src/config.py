"""Zentrale Konstanten und Konfiguration des Prototyps.

Quelle: docs/specifications/07_projektstruktur_claude_code.md (Abschnitt 7)
sowie 00_projektauftrag.md (Jahres- und Rundungslogik).

Die Jahreswerte (Y+1 usw.) werden NICHT hart codiert, sondern spaeter aus dem
aktuellen Jahr abgeleitet. Fuer Tests soll die Jahreslogik parametrisierbar sein.
"""

from pathlib import Path

# Verzeichnisse
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PFC_DIR = DATA_DIR / "pfc"

# Datenbank
DB_PATH = DATA_DIR / "app.db"
DB_BACKUP_PATH = DATA_DIR / "app_initial_backup.db"
DB_URL = f"sqlite:///{DB_PATH}"

# Excel-Mockdatenimport (siehe docs/specifications/06_excel_mockdaten_import.md)
MOCK_EXCEL_PATH = DATA_DIR / "mockdaten.xlsm"

# Fachliche Konstanten
POSITION_LIMIT_MW = 1.0

# Reihenfolge der Preisprodukte in der Pflegetabelle (relative Jahres-Offsets)
PRICE_PRODUCT_ORDER_TABLE = [
    ("Base", "Y+1"),
    ("Base", "Y+2"),
    ("Base", "Y+3"),
    ("Peak", "Y+1"),
    ("Peak", "Y+2"),
    ("Peak", "Y+3"),
]

# Reihenfolge der Preisprodukte im Chat-/Mailtext
PRICE_PRODUCT_ORDER_TEXT = [
    ("Base", "Y+1"),
    ("Peak", "Y+1"),
    ("Base", "Y+2"),
    ("Peak", "Y+2"),
    ("Base", "Y+3"),
    ("Peak", "Y+3"),
]
