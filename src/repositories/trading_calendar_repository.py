"""Repository fuer trading_calendar."""

import datetime as dt

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import TradingCalendarEntry
from src.domain.trading_calendar_logic import (
    STATUS_DELETED,
    STATUS_DONE,
    STATUS_PLANNED,
)


def list_visible_calendar_entries(session: Session) -> list[TradingCalendarEntry]:
    """Liefert alle nicht erledigten/geloeschten Eintraege, faelligste zuerst."""
    stmt = (
        select(TradingCalendarEntry)
        .where(TradingCalendarEntry.status.notin_((STATUS_DONE, STATUS_DELETED)))
        .order_by(TradingCalendarEntry.due_date.asc())
    )
    return list(session.scalars(stmt))


def get_calendar_entry(session: Session, entry_id: int) -> TradingCalendarEntry | None:
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
    last_modified_by: str = "system",
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
        last_modified_by=last_modified_by,
    )
    session.add(entry)
    session.flush()
    return entry


def set_status(
    session: Session, entry_id: int, status: str, last_modified_by: str = "system"
) -> TradingCalendarEntry | None:
    """Setzt Status und letzten Bearbeiter eines Kalendereintrags (kein Commit)."""
    entry = session.get(TradingCalendarEntry, entry_id)
    if entry is not None:
        entry.status = status
        entry.last_modified_by = last_modified_by
    return entry
