"""Tests fuer die Backup-Logik des Initialisierungs-Service (Arbeitspaket 2/Fix).

Regressionsabsicherung fuer den Fall, dass eine bereits initialisierte
Datenbank kein Backup besitzt (z. B. Abbruch zwischen Seed und Backup oder
nachtraeglich geloeschte Backup-Datei).
"""

from pathlib import Path

import src.services.initialization_service as init_service


def _redirect_paths(monkeypatch, tmp_path: Path) -> tuple[Path, Path]:
    db_path = tmp_path / "app.db"
    backup_path = tmp_path / "app_initial_backup.db"
    monkeypatch.setattr(init_service, "DB_PATH", db_path)
    monkeypatch.setattr(init_service, "DB_BACKUP_PATH", backup_path)
    return db_path, backup_path


def test_create_initial_backup_when_missing(monkeypatch, tmp_path):
    db_path, backup_path = _redirect_paths(monkeypatch, tmp_path)
    db_path.write_bytes(b"seeded-db-content")

    created = init_service.create_initial_backup()

    assert created is True
    assert backup_path.exists()
    assert backup_path.read_bytes() == b"seeded-db-content"


def test_create_initial_backup_is_noop_when_present(monkeypatch, tmp_path):
    db_path, backup_path = _redirect_paths(monkeypatch, tmp_path)
    db_path.write_bytes(b"new-content")
    backup_path.write_bytes(b"original-backup")

    created = init_service.create_initial_backup()

    # Bestehendes Backup darf nicht ueberschrieben werden.
    assert created is False
    assert backup_path.read_bytes() == b"original-backup"


def test_create_initial_backup_without_db_returns_false(monkeypatch, tmp_path):
    _, backup_path = _redirect_paths(monkeypatch, tmp_path)

    created = init_service.create_initial_backup()

    assert created is False
    assert not backup_path.exists()
