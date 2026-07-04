"""SQLAlchemy Engine und Session-Handling.

SQLite ist im Prototyp die zentrale Mock-Datenschicht, siehe
docs/specifications/02_datenmodell_sqlite.md.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import DATA_DIR, DB_URL


class Base(DeclarativeBase):
    """Gemeinsame Basisklasse fuer alle SQLAlchemy-Modelle."""


DATA_DIR.mkdir(parents=True, exist_ok=True)

# check_same_thread=False, da Streamlit die App-Skripte in Worker-Threads
# ausfuehrt und dasselbe Engine-Objekt ueber Reruns hinweg wiederverwendet.
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
