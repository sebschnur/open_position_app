"""Repository fuer trading_calendar."""

import datetime as dt
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import TradingCalendarEntry
from src.domain.trading_calendar_logic import STATUS_DONE, STATUS_PLANNED


def list_visible_calendar_entries(session: Session) -> List[TradingCalendarEntry]:
    """Liefert alle nicht erledigten Eintraege, faelligste zuerst."""
    stmt = (
        select(TradingCalendarEntry)
        .where(TradingCalendarEntry.status != STATUS_DONE)
        .order_by(TradingCalendarEntry.due_date.asc())
    )
    return list(session.scalars(stmt))


def get_calendar_entry(session: Session, entry_id: int) -> Optional[TradingCalendarEntry]:
    return session.get(TradingCalendarEntry, entry_id)


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
) -> TradingCalendarEntry:
    """Legt einen neuen Handelskalendereintrag an (kein Commit - Aufrufer entscheidet)."""
    entry = TradingCalendarEntry(
        due_date=due_date,
        partner_alias=partner_alias,
        direction=direction,
        quantity_y0_mwh=quantity_y0_mwh,
        quantity_y1_mwh=quantity_y1_mwh,
        quantity_y2_mwh=quantity_y2_mwh,
        quantity_y3_mwh=quantity_y3_mwh,
        quantity_y4_mwh=quantity_y4_mwh,
        status=STATUS_PLANNED,
    )
    session.add(entry)
    session.flush()
    return entry


def set_status(session: Session, entry_id: int, status: str) -> Optional[TradingCalendarEntry]:
    """Setzt den Status eines Handelskalendereintrags (kein Commit - Aufrufer entscheidet)."""
    entry = session.get(TradingCalendarEntry, entry_id)
    if entry is not None:
        entry.status = status
    return entry
