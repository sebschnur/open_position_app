"""Koordiniert DB-Initialisierung, Default-Seed und initiales Backup.

Workflow: docs/specifications/04_workflows_automatisierungen.md, Abschnitt 2.
Wird sowohl beim App-Start (app.py) als auch von den CLI-Skripten genutzt,
damit beide Wege denselben Ablauf verwenden.
"""

import datetime as dt
import shutil

from sqlalchemy.orm import Session

from src.config import DB_BACKUP_PATH, DB_PATH
from src.db.database import SessionLocal
from src.db.init_db import init_db
from src.db.models import AppMetadata
from src.db.seed_default_mock_data import seed_default_mock_data


def is_database_seeded(session: Session) -> bool:
    """Prueft anhand von app_metadata, ob die DB bereits initial befuellt wurde."""
    flag = session.get(AppMetadata, "db_initialized")
    return flag is not None and flag.value == "true"


def create_initial_backup() -> bool:
    """Kopiert den aktuellen DB-Stand einmalig nach app_initial_backup.db.

    Eine bereits vorhandene Backup-Datei wird nicht ueberschrieben.
    """
    if DB_PATH.exists() and not DB_BACKUP_PATH.exists():
        shutil.copyfile(DB_PATH, DB_BACKUP_PATH)
        return True
    return False


def _record_backup_timestamp() -> None:
    """Vermerkt den Zeitpunkt der Backup-Erzeugung in app_metadata."""
    with SessionLocal() as session:
        now = dt.datetime.utcnow()
        entry = session.get(AppMetadata, "initial_backup_created_at")
        if entry is None:
            session.add(
                AppMetadata(key="initial_backup_created_at", value=now.isoformat(), updated_at=now)
            )
        else:
            entry.value = now.isoformat()
            entry.updated_at = now
        session.commit()


def ensure_database_ready() -> str:
    """Stellt sicher, dass die DB existiert, befuellt ist und ein Backup hat.

    Eine bereits initialisierte Datenbank wird nicht stillschweigend erneut
    befuellt oder ueberschrieben.
    """
    init_db()

    newly_seeded = False
    with SessionLocal() as session:
        if not is_database_seeded(session):
            seed_default_mock_data(session)
            session.commit()
            newly_seeded = True

    # Backup unabhaengig vom Seed-Zweig sicherstellen: schliesst die Luecke,
    # falls ein frueherer Lauf zwischen Seed-Commit und Backup abgebrochen ist
    # oder die Backup-Datei nachtraeglich fehlt. create_initial_backup() ist
    # idempotent und legt nichts an, wenn bereits ein Backup existiert.
    if create_initial_backup():
        _record_backup_timestamp()

    if newly_seeded:
        return "Datenbank war leer und wurde mit Default-Mockdaten initialisiert."
    return "Bestehende Datenbank wird verwendet (bereits initialisiert)."
