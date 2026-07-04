"""Repository fuer limit_orders."""

import datetime as dt
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import LimitOrder

STATUS_OPEN = "offen"
STATUS_EXECUTED = "ausgeführt"
STATUS_DELETED = "gelöscht"
STATUS_EXPIRED = "abgelaufen"


def list_open_limit_orders(session: Session) -> List[LimitOrder]:
    """Liefert alle offenen Limitorders, neueste zuerst."""
    stmt = select(LimitOrder).where(LimitOrder.status == STATUS_OPEN).order_by(LimitOrder.id.desc())
    return list(session.scalars(stmt))


def get_limit_order(session: Session, order_id: int) -> Optional[LimitOrder]:
    return session.get(LimitOrder, order_id)


def add_limit_order(
    session: Session,
    partner_alias: str,
    quantity_y0_mwh: float,
    quantity_y1_mwh: float,
    quantity_y2_mwh: float,
    quantity_y3_mwh: float,
    quantity_y4_mwh: float,
    trigger_product_type: str,
    trigger_delivery_year: int,
    trigger_condition: str,
    limit_price_eur_mwh: float,
    responsible_trading: str,
    responsible_sales: str,
    valid_until: Optional[dt.date] = None,
) -> LimitOrder:
    """Legt eine neue Limitorder an (kein Commit - Aufrufer entscheidet)."""
    order = LimitOrder(
        partner_alias=partner_alias,
        quantity_y0_mwh=quantity_y0_mwh,
        quantity_y1_mwh=quantity_y1_mwh,
        quantity_y2_mwh=quantity_y2_mwh,
        quantity_y3_mwh=quantity_y3_mwh,
        quantity_y4_mwh=quantity_y4_mwh,
        trigger_product_type=trigger_product_type,
        trigger_delivery_year=trigger_delivery_year,
        trigger_condition=trigger_condition,
        limit_price_eur_mwh=limit_price_eur_mwh,
        responsible_trading=responsible_trading,
        responsible_sales=responsible_sales,
        valid_until=valid_until,
        status=STATUS_OPEN,
    )
    session.add(order)
    session.flush()
    return order


def set_status(session: Session, order_id: int, status: str) -> Optional[LimitOrder]:
    """Setzt den Status einer Limitorder (kein Commit - Aufrufer entscheidet)."""
    order = session.get(LimitOrder, order_id)
    if order is not None:
        order.status = status
    return order
