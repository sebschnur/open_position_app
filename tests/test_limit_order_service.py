"""Tests fuer den Limitorder-Service (Arbeitspaket 6).

Nutzt eine isolierte In-Memory-SQLite-Datenbank, um die reale app.db nicht
zu beruehren.
"""

import datetime as dt

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import Base
from src.db.models import IntradayTrade, MarketPrice
from src.domain.limit_order_logic import TRIGGER_PARTNER_BUYS_LT, TRIGGER_PARTNER_SELLS_GT
from src.services.limit_order_service import (
    add_limit_order,
    get_open_limit_order_rows,
    mark_deleted,
    mark_executed,
)

TODAY = dt.date(2026, 7, 4)
CURRENT_YEAR = TODAY.year
Y1 = CURRENT_YEAR + 1


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    with TestSession() as s:
        yield s


def _add_market_price(session, product_type, year, price):
    session.add(
        MarketPrice(
            product_type=product_type,
            delivery_year=year,
            price_eur_mwh=price,
            price_timestamp=dt.datetime(2026, 7, 4, 8, 0, 0),
        )
    )
    session.commit()


def test_add_limit_order_rejects_sign_mismatch(session):
    errors = add_limit_order(
        session,
        partner_alias="Testkunde",
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=-1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
        trigger_product_type="Base",
        trigger_delivery_year=Y1,
        trigger_condition=TRIGGER_PARTNER_BUYS_LT,
        limit_price_eur_mwh=90.0,
        responsible_trading="Handel A",
        responsible_sales="Vertrieb B",
    )

    assert errors
    assert get_open_limit_order_rows(session) == []


def test_add_limit_order_rejects_all_zero_quantities(session):
    errors = add_limit_order(
        session,
        partner_alias="Testkunde",
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=0.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
        trigger_product_type="Base",
        trigger_delivery_year=Y1,
        trigger_condition=TRIGGER_PARTNER_BUYS_LT,
        limit_price_eur_mwh=90.0,
        responsible_trading="Handel A",
        responsible_sales="Vertrieb B",
    )

    assert errors


def test_add_limit_order_saves_valid_order(session):
    errors = add_limit_order(
        session,
        partner_alias="Testkunde",
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
        trigger_product_type="Base",
        trigger_delivery_year=Y1,
        trigger_condition=TRIGGER_PARTNER_BUYS_LT,
        limit_price_eur_mwh=90.0,
        responsible_trading="Handel A",
        responsible_sales="Vertrieb B",
        valid_until=TODAY + dt.timedelta(days=30),
    )

    assert errors == []
    rows = get_open_limit_order_rows(session)
    assert len(rows) == 1
    assert rows[0].partner_alias == "Testkunde"
    assert rows[0].quantity_y1_mwh == 1000.0
    assert rows[0].trigger_label == f"Base {Y1}"
    assert rows[0].status == "offen"


def test_open_limit_order_rows_flags_triggered_condition(session):
    _add_market_price(session, "Base", Y1, 85.0)
    add_limit_order(
        session,
        partner_alias="Testkunde",
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
        trigger_product_type="Base",
        trigger_delivery_year=Y1,
        trigger_condition=TRIGGER_PARTNER_BUYS_LT,
        limit_price_eur_mwh=90.0,
        responsible_trading="Handel A",
        responsible_sales="Vertrieb B",
    )

    rows = get_open_limit_order_rows(session)

    assert rows[0].current_market_price_eur_mwh == pytest.approx(85.0)
    assert rows[0].is_triggered is True


def test_open_limit_order_rows_not_triggered_without_market_price(session):
    add_limit_order(
        session,
        partner_alias="Testkunde",
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
        trigger_product_type="Base",
        trigger_delivery_year=Y1,
        trigger_condition=TRIGGER_PARTNER_BUYS_LT,
        limit_price_eur_mwh=90.0,
        responsible_trading="Handel A",
        responsible_sales="Vertrieb B",
    )

    rows = get_open_limit_order_rows(session)

    assert rows[0].current_market_price_eur_mwh is None
    assert rows[0].is_triggered is False


def test_mark_executed_creates_intraday_trade_and_updates_status(session):
    add_limit_order(
        session,
        partner_alias="Testkunde",
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
        trigger_product_type="Base",
        trigger_delivery_year=Y1,
        trigger_condition=TRIGGER_PARTNER_BUYS_LT,
        limit_price_eur_mwh=90.0,
        responsible_trading="Handel A",
        responsible_sales="Vertrieb B",
    )
    order_id = get_open_limit_order_rows(session)[0].id

    mark_executed(session, order_id, today=TODAY)

    assert get_open_limit_order_rows(session) == []
    trades = session.query(IntradayTrade).all()
    assert len(trades) == 1
    trade = trades[0]
    assert trade.partner_alias == "Testkunde"
    assert trade.quantity_y1_mwh == 1000.0
    assert trade.trade_date == TODAY
    assert trade.source_type == "limit_order"
    assert trade.source_id == order_id


def test_mark_executed_is_noop_when_order_already_closed(session):
    add_limit_order(
        session,
        partner_alias="Testkunde",
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=-1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
        trigger_product_type="Base",
        trigger_delivery_year=Y1,
        trigger_condition=TRIGGER_PARTNER_SELLS_GT,
        limit_price_eur_mwh=90.0,
        responsible_trading="Handel A",
        responsible_sales="Vertrieb B",
    )
    order_id = get_open_limit_order_rows(session)[0].id

    mark_executed(session, order_id, today=TODAY)
    mark_executed(session, order_id, today=TODAY)

    trades = session.query(IntradayTrade).all()
    assert len(trades) == 1


def test_mark_deleted_removes_order_from_open_list(session):
    add_limit_order(
        session,
        partner_alias="Testkunde",
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
        trigger_product_type="Base",
        trigger_delivery_year=Y1,
        trigger_condition=TRIGGER_PARTNER_BUYS_LT,
        limit_price_eur_mwh=90.0,
        responsible_trading="Handel A",
        responsible_sales="Vertrieb B",
    )
    order_id = get_open_limit_order_rows(session)[0].id

    mark_deleted(session, order_id)

    assert get_open_limit_order_rows(session) == []
