"""Repository fuer app_metadata."""

import datetime as dt

from sqlalchemy.orm import Session

from src.db.models import AppMetadata


def get_metadata(session: Session, key: str) -> AppMetadata | None:
    return session.get(AppMetadata, key)


def upsert_metadata(
    session: Session, key: str, value: str, now: dt.datetime
) -> AppMetadata:
    """Legt einen Metadaten-Eintrag an oder aktualisiert ihn (kein Commit)."""
    entry = session.get(AppMetadata, key)
    if entry is None:
        entry = AppMetadata(key=key, value=value, updated_at=now)
        session.add(entry)
    else:
        entry.value = value
        entry.updated_at = now
    return entry
