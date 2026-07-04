"""Repository fuer intraday_trades."""

import datetime as dt
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import IntradayTrade


def list_intraday_trades(session: Session) -> List[IntradayTrade]:
    """Liefert alle untertaegigen Geschaefte, neueste zuerst."""
    stmt = select(IntradayTrade).order_by(IntradayTrade.trade_date.desc(), IntradayTrade.id.desc())
    return list(session.scalars(stmt))


def add_intraday_trade(
    session: Session,
    trade_date: dt.date,
    partner_alias: str,
    quantity_y0_mwh: float,
    quantity_y1_mwh: float,
    quantity_y2_mwh: float,
    quantity_y3_mwh: float,
    quantity_y4_mwh: float,
    source_type: str,
    source_id: Optional[int] = None,
) -> IntradayTrade:
    """Legt ein neues untertaegiges Geschaeft an (kein Commit - Aufrufer entscheidet)."""
    trade = IntradayTrade(
        trade_date=trade_date,
        partner_alias=partner_alias,
        quantity_y0_mwh=quantity_y0_mwh,
        quantity_y1_mwh=quantity_y1_mwh,
        quantity_y2_mwh=quantity_y2_mwh,
        quantity_y3_mwh=quantity_y3_mwh,
        quantity_y4_mwh=quantity_y4_mwh,
        source_type=source_type,
        source_id=source_id,
    )
    session.add(trade)
    session.flush()
    return trade


def delete_intraday_trade(session: Session, trade_id: int) -> None:
    """Loescht ein untertaegiges Geschaeft physisch (keine Historisierung im Prototyp)."""
    trade = session.get(IntradayTrade, trade_id)
    if trade is not None:
        session.delete(trade)
