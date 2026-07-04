"""Positions- und Limitlogik.

Vorgabe: docs/specifications/01_fachliche_funktionen.md (Abschnitt 5),
04_workflows_automatisierungen.md (Abschnitt 3). Reine Funktionen.

Die eigentliche Aggregation ueber DB-Daten (PMS-Position + untertaegige
Geschaefte je Jahr) erfolgt im Position-Service (Arbeitspaket 4). Hier liegen
nur die reinen Rechenregeln.
"""

from src.config import POSITION_LIMIT_MW

STATUS_WITHIN_LIMIT = "innerhalb Limit"
STATUS_LIMIT_BREACHED = "Limit überschritten"


def simulated_position_mw(pms_position_mw: float, intraday_position_mw: float) -> float:
    """Simulierte Position = PMS-Position + Nettoeffekt untertaegiger Geschaefte."""
    return pms_position_mw + intraday_position_mw


def is_limit_breached(position_mw: float, limit_mw: float = POSITION_LIMIT_MW) -> bool:
    """Limit gilt je Kalenderjahr auf den Absolutwert: verletzt, wenn abs(pos) > limit."""
    return abs(position_mw) > limit_mw


def utilization_pct(position_mw: float, limit_mw: float = POSITION_LIMIT_MW) -> float:
    """Limitauslastung in Prozent: abs(position_mw) / limit_mw * 100."""
    return abs(position_mw) / limit_mw * 100


def limit_status(position_mw: float, limit_mw: float = POSITION_LIMIT_MW) -> str:
    """Statustext fuer die Positionstabelle."""
    return STATUS_LIMIT_BREACHED if is_limit_breached(position_mw, limit_mw) else STATUS_WITHIN_LIMIT
