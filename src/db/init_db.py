"""Datenbank-Schema erzeugen.

create_all() legt nur fehlende Tabellen an und ueberschreibt keine
vorhandenen Daten - eine bestehende Datenbank bleibt unangetastet.

Zusaetzlich wird eine leichte Migration ausgefuehrt, die die Spalte
``last_modified_by`` (Nachvollziehbarkeit manueller Eintraege) in bereits
bestehenden Tabellen nachtraeglich ergaenzt. create_all() kann fehlende
Spalten naemlich nicht nachziehen.
"""

from src.config import DATA_DIR, DB_PATH
from src.db import models  # noqa: F401  (registriert die Modelle auf Base.metadata)
from src.db.database import Base, engine

# Tabellen mit manuellen Eintraegen, die eine last_modified_by-Spalte fuehren.
_LAST_MODIFIED_BY_TABLES = (
    "intraday_trades",
    "market_prices",
    "otc_surcharges",
    "limit_orders",
    "trading_calendar",
)


def _ensure_last_modified_by_columns() -> None:
    """Ergaenzt fehlende last_modified_by-Spalten in bestehenden Tabellen."""
    with engine.begin() as conn:
        for table in _LAST_MODIFIED_BY_TABLES:
            columns = {row[1] for row in conn.exec_driver_sql(f"PRAGMA table_info({table})")}
            if not columns:
                continue  # Tabelle existiert (noch) nicht - create_all legt sie neu an.
            if "last_modified_by" not in columns:
                conn.exec_driver_sql(
                    f"ALTER TABLE {table} "
                    "ADD COLUMN last_modified_by VARCHAR(120) NOT NULL DEFAULT 'system'"
                )


def init_db() -> bool:
    """Erzeugt das DB-Schema, falls noch nicht vorhanden.

    Gibt zurueck, ob die Datenbankdatei vor dem Aufruf bereits existierte.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_existed = DB_PATH.exists()
    Base.metadata.create_all(bind=engine)
    _ensure_last_modified_by_columns()
    return db_existed
