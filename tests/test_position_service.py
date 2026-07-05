"""Tests fuer den Position-Service (Arbeitspaket 4).

Nutzt eine isolierte In-Memory-SQLite-Datenbank, um die reale app.db nicht
zu beruehren.
"""

import datetime as dt

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import Base
from src.db.models import PortfolioPosition
from src.services.position_service import (
    add_intraday_trade,
    delete_intraday_trade,
    get_intraday_trade_rows,
    get_position_table,
)

TODAY = dt.date(2026, 7, 4)
CURRENT_YEAR = TODAY.year


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    with TestSession() as s:
        yield s


def _seed_pms_position(session, year, position_mwh):
    session.add(
        PortfolioPosition(as_of_date=TODAY, year=year, position_mwh=position_mwh, source="test")
    )
    session.commit()


def test_position_table_without_intraday_trades(session):
    _seed_pms_position(session, CURRENT_YEAR + 1, 8760)  # normales Jahr -> exakt 1 MW

    rows = get_position_table(session, today=TODAY)

    row_y1 = next(r for r in rows if r.year == CURRENT_YEAR + 1)
    assert row_y1.pms_position_mw == pytest.approx(1.0)
    assert row_y1.intraday_position_mw == 0.0
    assert row_y1.simulated_position_mw == pytest.approx(1.0)
    assert row_y1.status == "innerhalb Limit"


def test_position_table_covers_y0_to_y4(session):
    rows = get_position_table(session, today=TODAY)
    assert [r.year for r in rows] == [CURRENT_YEAR + i for i in range(5)]


def test_intraday_trade_shifts_simulated_position_and_breaches_limit(session):
    _seed_pms_position(session, CURRENT_YEAR + 1, 8760)  # 1 MW

    errors = add_intraday_trade(
        session,
        trade_date=TODAY,
        partner_alias="Testpartner",
        quantity_y0_mwh=0,
        quantity_y1_mwh=8760,  # weiteres +1 MW -> Summe 2 MW, Limit verletzt
        quantity_y2_mwh=0,
        quantity_y3_mwh=0,
        quantity_y4_mwh=0,
    )
    assert errors == []

    rows = get_position_table(session, today=TODAY)
    row_y1 = next(r for r in rows if r.year == CURRENT_YEAR + 1)
    assert row_y1.simulated_position_mw == pytest.approx(2.0)
    assert row_y1.status == "Limit überschritten"


def test_add_intraday_trade_requires_nonzero_quantity(session):
    errors = add_intraday_trade(
        session,
        trade_date=TODAY,
        partner_alias="Testpartner",
        quantity_y0_mwh=0,
        quantity_y1_mwh=0,
        quantity_y2_mwh=0,
        quantity_y3_mwh=0,
        quantity_y4_mwh=0,
    )
    assert len(errors) == 1
    assert "ungleich 0" in errors[0]


def test_intraday_trade_with_mixed_signs_is_not_reported_as_no_quantity(session):
    # Regressionsfall aus dem Code-Review: +5000 in Y1 und -5000 in Y2
    # summieren sich zu 0, duerfen aber NICHT als "Keine Menge" erscheinen,
    # da beide Jahre echte, nur gegenlaeufige Positionswirkungen haben.
    add_intraday_trade(
        session,
        trade_date=TODAY,
        partner_alias="Testpartner",
        quantity_y0_mwh=0,
        quantity_y1_mwh=5000,
        quantity_y2_mwh=-5000,
        quantity_y3_mwh=0,
        quantity_y4_mwh=0,
    )

    trade_rows = get_intraday_trade_rows(session)
    assert len(trade_rows) == 1
    assert trade_rows[0].interpretation == "Gemischte Vorzeichen - Jahresmengen pruefen"


def test_add_intraday_trade_stores_username_as_last_modified_by(session):
    add_intraday_trade(
        session,
        trade_date=TODAY,
        partner_alias="Testpartner",
        quantity_y0_mwh=0,
        quantity_y1_mwh=1000,
        quantity_y2_mwh=0,
        quantity_y3_mwh=0,
        quantity_y4_mwh=0,
        username="anna",
    )

    trade_rows = get_intraday_trade_rows(session)
    assert trade_rows[0].last_modified_by == "anna"


def test_intraday_trade_interpretation_and_delete(session):
    add_intraday_trade(
        session,
        trade_date=TODAY,
        partner_alias="Testpartner",
        quantity_y0_mwh=0,
        quantity_y1_mwh=-5000,
        quantity_y2_mwh=0,
        quantity_y3_mwh=0,
        quantity_y4_mwh=0,
    )

    trade_rows = get_intraday_trade_rows(session)
    assert len(trade_rows) == 1
    assert trade_rows[0].interpretation == "Partner verkauft an uns"
    assert trade_rows[0].quantity_y1_mwh == -5000.0

    delete_intraday_trade(session, trade_rows[0].id)
    assert get_intraday_trade_rows(session) == []
