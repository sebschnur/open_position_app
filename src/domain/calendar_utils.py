"""Kalender-Hilfsfunktionen.

Vorgabe: docs/specifications/02_datenmodell_sqlite.md (Abschnitt 14).
Reine Funktionen ohne Streamlit-/DB-Abhaengigkeit.
"""


def is_leap_year(year: int) -> bool:
    """Erkennt Schaltjahre nach dem gregorianischen Kalender."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def hours_in_year(year: int) -> int:
    """Stunden eines Kalenderjahres: 8.784 im Schaltjahr, sonst 8.760."""
    return 8784 if is_leap_year(year) else 8760
