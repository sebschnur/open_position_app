"""Datenbank-Schema erzeugen.

create_all() legt nur fehlende Tabellen an und ueberschreibt keine
vorhandenen Daten - eine bestehende Datenbank bleibt unangetastet.
"""

from src.config import DATA_DIR, DB_PATH
from src.db import models  # noqa: F401  (registriert die Modelle auf Base.metadata)
from src.db.database import Base, engine


def init_db() -> bool:
    """Erzeugt das DB-Schema, falls noch nicht vorhanden.

    Gibt zurueck, ob die Datenbankdatei vor dem Aufruf bereits existierte.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db_existed = DB_PATH.exists()
    Base.metadata.create_all(bind=engine)
    return db_existed
