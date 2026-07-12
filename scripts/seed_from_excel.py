"""CLI: DB aus Excel-Mockdaten und PFC-Dateien befuellen.

Aufruf:
    python scripts/seed_from_excel.py --excel data/mockdaten.xlsm --db data/app.db --pfc-dir data/pfc

Umsetzung: 06_excel_mockdaten_import.md. Eine bereits initialisierte
Datenbank wird NICHT stillschweigend ueberschrieben. Fehlende Werte werden
als klar gekennzeichnete Default-Mockdaten erzeugt (siehe Importprotokoll).
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import DB_BACKUP_PATH, DB_PATH, MOCK_EXCEL_PATH, PFC_DIR  # noqa: E402
from src.db.database import SessionLocal  # noqa: E402
from src.db.init_db import init_db  # noqa: E402
from src.services.excel_import_service import seed_database_from_excel  # noqa: E402
from src.services.initialization_service import create_initial_backup  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Excel-/PFC-Mockdatenimport")
    parser.add_argument(
        "--excel", type=Path, default=MOCK_EXCEL_PATH, help="Pfad zur Excel-Mockdatei"
    )
    parser.add_argument(
        "--db", type=Path, default=DB_PATH, help="Pfad zur SQLite-Datenbank"
    )
    parser.add_argument(
        "--pfc-dir", type=Path, default=PFC_DIR, help="Verzeichnis mit PFC-Dateien"
    )
    args = parser.parse_args()

    if args.db != DB_PATH:
        print(
            f"Hinweis: --db wird in diesem Prototyp ignoriert, es wird immer die "
            f"konfigurierte Datenbank verwendet: {DB_PATH}"
        )

    if not args.excel.exists():
        raise SystemExit(f"Excel-Mockdatei nicht gefunden: {args.excel}")

    init_db()

    with SessionLocal() as session:
        report = seed_database_from_excel(
            session, excel_path=args.excel, pfc_dir=args.pfc_dir
        )
        if report.already_seeded:
            print(
                "Datenbank ist bereits initialisiert - Excel-Import wird nicht durchgefuehrt."
            )
            return
        session.commit()

    if report.warnings:
        print(f"Import abgeschlossen mit {len(report.warnings)} Hinweis(en):")
        for warning in report.warnings:
            print(f"  - {warning}")
    else:
        print("Import abgeschlossen ohne Hinweise.")

    if create_initial_backup():
        print(f"Initiales Backup erzeugt: {DB_BACKUP_PATH}")


if __name__ == "__main__":
    main()
