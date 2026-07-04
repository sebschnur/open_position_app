"""Service: Handelskalender.

Vorgabe: docs/specifications/01_fachliche_funktionen.md (Abschnitt 12),
03_streamlit_ui_konzept.md (Abschnitt 7), 04_workflows_automatisierungen.md
(Abschnitt 13-15).

Der Anzeigestatus "fällig" ist keine dauerhaft gespeicherte Statuswert,
sondern wird je Anfrage aus due_date/status berechnet (is_due). Persistiert
werden nur "geplant" und "erledigt". Die Faelligkeitspruefung ist reine
Hervorhebung - analog zur Limitorder-Ausloeseanzeige gibt es keine Sperre:
"Erledigt" kann fuer jeden sichtbaren Eintrag geklickt werden, unabhaengig
davon, ob er bereits faellig ist (Nutzer trifft die finale Entscheidung).
"""

import datetime as dt
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.quantity_utils import round_mwh
from src.domain.trading_calendar_logic import (
    DIRECTION_LABELS,
    STATUS_DONE,
    STATUS_DUE,
    is_due,
)
from src.domain.validation import expected_sign_for_direction, validate_trade_quantities
from src.repositories.intraday_trade_repository import (
    add_intraday_trade as _repo_add_intraday_trade,
)
from src.repositories.trading_calendar_repository import (
    add_calendar_entry as _repo_add_calendar_entry,
)
from src.repositories.trading_calendar_repository import (
    get_calendar_entry,
    list_visible_calendar_entries,
    set_status,
)


@dataclass
class TradingCalendarRow:
    id: int
    due_date: dt.date
    partner_alias: str
    direction_label: str
    quantity_y0_mwh: float
    quantity_y1_mwh: float
    quantity_y2_mwh: float
    quantity_y3_mwh: float
    quantity_y4_mwh: float
    display_status: str
    is_due: bool


def get_visible_calendar_rows(
    session: Session, today: Optional[dt.date] = None
) -> List[TradingCalendarRow]:
    """Liefert alle nicht erledigten Kalendereintraege inkl. Faelligkeitsstatus."""
    today = today or dt.date.today()
    rows = []
    for entry in list_visible_calendar_entries(session):
        due_flag = is_due(entry.due_date, entry.status, today)
        rows.append(
            TradingCalendarRow(
                id=entry.id,
                due_date=entry.due_date,
                partner_alias=entry.partner_alias,
                direction_label=DIRECTION_LABELS[entry.direction],
                quantity_y0_mwh=round_mwh(entry.quantity_y0_mwh),
                quantity_y1_mwh=round_mwh(entry.quantity_y1_mwh),
                quantity_y2_mwh=round_mwh(entry.quantity_y2_mwh),
                quantity_y3_mwh=round_mwh(entry.quantity_y3_mwh),
                quantity_y4_mwh=round_mwh(entry.quantity_y4_mwh),
                display_status=STATUS_DUE if due_flag else entry.status,
                is_due=due_flag,
            )
        )
    return rows


def add_calendar_entry(
    session: Session,
    due_date: dt.date,
    partner_alias: str,
    direction: str,
    quantity_y0_mwh: float,
    quantity_y1_mwh: float,
    quantity_y2_mwh: float,
    quantity_y3_mwh: float,
    quantity_y4_mwh: float,
) -> List[str]:
    """Validiert und speichert einen neuen Handelskalendereintrag.

    Gibt eine Liste von Validierungsfehlern zurueck (leer = erfolgreich
    gespeichert und committet).
    """
    quantities = [
        round_mwh(quantity_y0_mwh),
        round_mwh(quantity_y1_mwh),
        round_mwh(quantity_y2_mwh),
        round_mwh(quantity_y3_mwh),
        round_mwh(quantity_y4_mwh),
    ]
    expected_sign = expected_sign_for_direction(direction)
    errors = validate_trade_quantities(quantities, expected_sign)
    if errors:
        return errors

    _repo_add_calendar_entry(
        session,
        due_date=due_date,
        partner_alias=partner_alias,
        direction=direction,
        quantity_y0_mwh=quantities[0],
        quantity_y1_mwh=quantities[1],
        quantity_y2_mwh=quantities[2],
        quantity_y3_mwh=quantities[3],
        quantity_y4_mwh=quantities[4],
    )
    session.commit()
    return []


def mark_done(session: Session, entry_id: int, today: Optional[dt.date] = None) -> None:
    """Erzeugt ein untertaegiges Geschaeft aus dem Kalendereintrag und setzt ihn auf 'erledigt'."""
    today = today or dt.date.today()
    entry = get_calendar_entry(session, entry_id)
    if entry is None or entry.status == STATUS_DONE:
        return

    _repo_add_intraday_trade(
        session,
        trade_date=today,
        partner_alias=entry.partner_alias,
        quantity_y0_mwh=entry.quantity_y0_mwh,
        quantity_y1_mwh=entry.quantity_y1_mwh,
        quantity_y2_mwh=entry.quantity_y2_mwh,
        quantity_y3_mwh=entry.quantity_y3_mwh,
        quantity_y4_mwh=entry.quantity_y4_mwh,
        source_type="trading_calendar",
        source_id=entry.id,
    )
    set_status(session, entry_id, STATUS_DONE)
    session.commit()
