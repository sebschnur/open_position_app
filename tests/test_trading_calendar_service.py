"""Tests fuer den Handelskalender-Service (Arbeitspaket 7).

Nutzt eine isolierte In-Memory-SQLite-Datenbank, um die reale app.db nicht
zu beruehren.
"""

import datetime as dt

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import Base
from src.db.models import IntradayTrade
from src.domain.validation import DIRECTION_PARTNER_BUYS, DIRECTION_PARTNER_SELLS
from src.services.trading_calendar_service import (
    add_calendar_entry,
    get_visible_calendar_rows,
    mark_deleted,
    mark_done,
)

TODAY = dt.date(2026, 7, 5)


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    with TestSession() as s:
        yield s


def test_add_calendar_entry_rejects_sign_mismatch(session):
    errors = add_calendar_entry(
        session,
        due_date=TODAY + dt.timedelta(days=7),
        partner_alias="Testkunde",
        direction=DIRECTION_PARTNER_BUYS,
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=-1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
    )

    assert errors
    assert get_visible_calendar_rows(session, today=TODAY) == []


def test_add_calendar_entry_rejects_all_zero_quantities(session):
    errors = add_calendar_entry(
        session,
        due_date=TODAY,
        partner_alias="Testkunde",
        direction=DIRECTION_PARTNER_BUYS,
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=0.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
    )

    assert errors


def test_add_calendar_entry_saves_valid_entry(session):
    errors = add_calendar_entry(
        session,
        due_date=TODAY + dt.timedelta(days=7),
        partner_alias="Testkunde",
        direction=DIRECTION_PARTNER_BUYS,
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
    )

    assert errors == []
    rows = get_visible_calendar_rows(session, today=TODAY)
    assert len(rows) == 1
    assert rows[0].partner_alias == "Testkunde"
    assert rows[0].direction_label == "Partner kauft"
    assert rows[0].quantity_y1_mwh == 1000.0
    assert rows[0].is_due is False
    assert rows[0].display_status == "geplant"


def test_visible_rows_flag_overdue_entry_as_due(session):
    add_calendar_entry(
        session,
        due_date=TODAY - dt.timedelta(days=3),
        partner_alias="Testkunde",
        direction=DIRECTION_PARTNER_SELLS,
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=-500.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
    )

    rows = get_visible_calendar_rows(session, today=TODAY)

    assert rows[0].is_due is True
    assert rows[0].display_status == "fällig"


def test_mark_done_creates_intraday_trade_and_hides_entry(session):
    add_calendar_entry(
        session,
        due_date=TODAY - dt.timedelta(days=1),
        partner_alias="Testkunde",
        direction=DIRECTION_PARTNER_BUYS,
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
    )
    entry_id = get_visible_calendar_rows(session, today=TODAY)[0].id

    mark_done(session, entry_id, today=TODAY)

    assert get_visible_calendar_rows(session, today=TODAY) == []
    trades = session.query(IntradayTrade).all()
    assert len(trades) == 1
    trade = trades[0]
    assert trade.partner_alias == "Testkunde"
    assert trade.quantity_y1_mwh == 1000.0
    assert trade.trade_date == TODAY
    assert trade.source_type == "trading_calendar"
    assert trade.source_id == entry_id


def test_mark_done_is_noop_when_entry_already_done(session):
    add_calendar_entry(
        session,
        due_date=TODAY,
        partner_alias="Testkunde",
        direction=DIRECTION_PARTNER_BUYS,
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
    )
    entry_id = get_visible_calendar_rows(session, today=TODAY)[0].id

    mark_done(session, entry_id, today=TODAY)
    mark_done(session, entry_id, today=TODAY)

    trades = session.query(IntradayTrade).all()
    assert len(trades) == 1


def test_mark_deleted_hides_entry_without_creating_trade(session):
    add_calendar_entry(
        session,
        due_date=TODAY - dt.timedelta(days=1),
        partner_alias="Testkunde",
        direction=DIRECTION_PARTNER_BUYS,
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
    )
    entry_id = get_visible_calendar_rows(session, today=TODAY)[0].id

    mark_deleted(session, entry_id)

    # Eintrag verschwindet aus der Standardansicht ...
    assert get_visible_calendar_rows(session, today=TODAY) == []
    # ... aber es wird KEIN untertaegiges Geschaeft erzeugt (keine Positionswirkung).
    assert session.query(IntradayTrade).all() == []


def test_mark_done_available_even_when_not_yet_due(session):
    add_calendar_entry(
        session,
        due_date=TODAY + dt.timedelta(days=30),
        partner_alias="Testkunde",
        direction=DIRECTION_PARTNER_BUYS,
        quantity_y0_mwh=0.0,
        quantity_y1_mwh=1000.0,
        quantity_y2_mwh=0.0,
        quantity_y3_mwh=0.0,
        quantity_y4_mwh=0.0,
    )
    entry_id = get_visible_calendar_rows(session, today=TODAY)[0].id

    mark_done(session, entry_id, today=TODAY)

    trades = session.query(IntradayTrade).all()
    assert len(trades) == 1
