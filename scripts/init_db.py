"""CLI: Datenbank-Schema erzeugen.

Aufruf:  python scripts/init_db.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import DB_PATH  # noqa: E402
from src.db.init_db import init_db  # noqa: E402


def main() -> None:
    db_existed = init_db()
    if db_existed:
        print(f"Datenbank existierte bereits: {DB_PATH}")
    else:
        print(f"Datenbank neu angelegt: {DB_PATH}")
    print("Schema (Tabellen) ist vorhanden.")


if __name__ == "__main__":
    main()
