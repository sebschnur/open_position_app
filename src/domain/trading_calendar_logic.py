"""Handelskalender-Logik.

Vorgabe: docs/specifications/01_fachliche_funktionen.md (Abschnitt 12),
03_streamlit_ui_konzept.md (Abschnitt 7.3/7.4),
04_workflows_automatisierungen.md (Abschnitt 13). Reine Funktionen.

Das heutige Datum ist injizierbar, damit Tests nicht vom echten Kalendertag
abhaengen.
"""

import datetime as dt
from typing import Optional

STATUS_PLANNED = "geplant"
STATUS_DUE = "faellig"
STATUS_DONE = "erledigt"


def _resolve_today(today: Optional[dt.date]) -> dt.date:
    return today if today is not None else dt.date.today()


def is_due(due_date: dt.date, status: str, today: Optional[dt.date] = None) -> bool:
    """Faellig, wenn Datum <= heute und Status != erledigt."""
    return due_date <= _resolve_today(today) and status != STATUS_DONE


def is_visible_in_standard_view(status: str) -> bool:
    """Standardansicht: alle nicht erledigten Eintraege (heutige, kuenftige, ueberfaellige).

    Erledigte Eintraege werden nicht angezeigt.
    """
    return status != STATUS_DONE
