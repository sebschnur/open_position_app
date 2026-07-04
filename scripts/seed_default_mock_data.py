"""CLI: Datenbank mit Default-Mockdaten befuellen und initiales Backup erzeugen.

Aufruf:  python scripts/seed_default_mock_data.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.services.initialization_service import ensure_database_ready  # noqa: E402


def main() -> None:
    status = ensure_database_ready()
    print(status)


if __name__ == "__main__":
    main()
