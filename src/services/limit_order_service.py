"""Service: Limitorder.

Vorgabe: docs/specifications/01_fachliche_funktionen.md (Abschnitt 11),
03_streamlit_ui_konzept.md (Abschnitt 6), 04_workflows_automatisierungen.md
(Abschnitt 10-12).

Die Pruefung gegen Marktpreise ist reine Anzeige/Hervorhebung - es gibt keine
automatische Ausfuehrung. Erst der Klick auf "Ausgefuehrt" erzeugt ein
untertaegiges Geschaeft (Quelle "limit_order") und setzt den Status.

Der Status "abgelaufen" wird bewusst NICHT automatisch gesetzt: laut
04_workflows_automatisierungen.md (Abschnitt 16) ist offen, ob dieser Status
automatisch oder manuell vergeben wird - das ist noch nicht fachlich geklaert.
"""

import datetime as dt
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.domain.limit_order_logic import TRIGGER_CONDITION_LABELS, is_triggered
from src.domain.quantity_utils import round_mwh
from src.domain.validation import (
    expected_sign_for_trigger_condition,
    validate_trade_quantities,
)
from src.repositories.intraday_trade_repository import (
    add_intraday_trade as _repo_add_intraday_trade,
)
from src.repositories.limit_order_repository import (
    STATUS_DELETED,
    STATUS_EXECUTED,
    STATUS_OPEN,
    get_limit_order,
    list_open_limit_orders,
    set_status,
)
from src.repositories.limit_order_repository import (
    add_limit_order as _repo_add_limit_order,
)
from src.repositories.price_repository import get_market_prices_by_product_year


@dataclass
class LimitOrderRow:
    id: int
    partner_alias: str
    quantity_y0_mwh: float
    quantity_y1_mwh: float
    quantity_y2_mwh: float
    quantity_y3_mwh: float
    quantity_y4_mwh: float
    trigger_label: str
    trigger_condition_label: str
    limit_price_eur_mwh: float
    current_market_price_eur_mwh: float | None
    is_triggered: bool
    last_modified_by: str
    valid_until: dt.date | None
    status: str


def get_open_limit_order_rows(session: Session) -> list[LimitOrderRow]:
    """Liefert alle offenen Limitorders inkl. Ausloese-Pruefung gegen aktuelle Marktpreise."""
    prices_by_key = get_market_prices_by_product_year(session)
    rows = []
    for order in list_open_limit_orders(session):
        market_price = prices_by_key.get(
            (order.trigger_product_type, order.trigger_delivery_year)
        )
        current_price = market_price.price_eur_mwh if market_price is not None else None
        triggered = current_price is not None and is_triggered(
            order.trigger_condition, current_price, order.limit_price_eur_mwh
        )
        rows.append(
            LimitOrderRow(
                id=order.id,
                partner_alias=order.partner_alias,
                quantity_y0_mwh=round_mwh(order.quantity_y0_mwh),
                quantity_y1_mwh=round_mwh(order.quantity_y1_mwh),
                quantity_y2_mwh=round_mwh(order.quantity_y2_mwh),
                quantity_y3_mwh=round_mwh(order.quantity_y3_mwh),
                quantity_y4_mwh=round_mwh(order.quantity_y4_mwh),
                trigger_label=f"{order.trigger_product_type} {order.trigger_delivery_year}",
                trigger_condition_label=TRIGGER_CONDITION_LABELS[
                    order.trigger_condition
                ],
                limit_price_eur_mwh=order.limit_price_eur_mwh,
                current_market_price_eur_mwh=current_price,
                is_triggered=triggered,
                last_modified_by=order.last_modified_by,
                valid_until=order.valid_until,
                status=order.status,
            )
        )
    return rows


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
    username: str = "system",
    valid_until: dt.date | None = None,
) -> list[str]:
    """Validiert und speichert eine neue Limitorder.

    ``username`` wird als letzter Bearbeiter gespeichert. Ein separates Feld
    "Verantwortlicher" gibt es nicht mehr - die Nachvollziehbarkeit erfolgt
    ausschliesslich ueber den Benutzernamen (last_modified_by).
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
    expected_sign = expected_sign_for_trigger_condition(trigger_condition)
    errors = validate_trade_quantities(quantities, expected_sign)
    if errors:
        return errors

    _repo_add_limit_order(
        session,
        partner_alias=partner_alias,
        quantity_y0_mwh=quantities[0],
        quantity_y1_mwh=quantities[1],
        quantity_y2_mwh=quantities[2],
        quantity_y3_mwh=quantities[3],
        quantity_y4_mwh=quantities[4],
        trigger_product_type=trigger_product_type,
        trigger_delivery_year=trigger_delivery_year,
        trigger_condition=trigger_condition,
        limit_price_eur_mwh=limit_price_eur_mwh,
        last_modified_by=username,
        valid_until=valid_until,
    )
    session.commit()
    return []


def mark_executed(
    session: Session,
    order_id: int,
    username: str = "system",
    today: dt.date | None = None,
) -> None:
    """Erzeugt ein untertaegiges Geschaeft aus der Limitorder und setzt sie auf 'ausgefuehrt'.

    ``username`` (der ausfuehrende Benutzer) ersetzt den bisherigen Bearbeiter.
    """
    today = today or dt.date.today()
    order = get_limit_order(session, order_id)
    if order is None or order.status != STATUS_OPEN:
        return

    _repo_add_intraday_trade(
        session,
        trade_date=today,
        partner_alias=order.partner_alias,
        quantity_y0_mwh=order.quantity_y0_mwh,
        quantity_y1_mwh=order.quantity_y1_mwh,
        quantity_y2_mwh=order.quantity_y2_mwh,
        quantity_y3_mwh=order.quantity_y3_mwh,
        quantity_y4_mwh=order.quantity_y4_mwh,
        source_type="limit_order",
        source_id=order.id,
        last_modified_by=username,
    )
    set_status(session, order_id, STATUS_EXECUTED, last_modified_by=username)
    session.commit()


def mark_deleted(session: Session, order_id: int, username: str = "system") -> None:
    """Setzt eine Limitorder auf 'geloescht'; ``username`` wird als Bearbeiter vermerkt."""
    set_status(session, order_id, STATUS_DELETED, last_modified_by=username)
    session.commit()
