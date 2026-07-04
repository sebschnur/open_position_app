"""Tests fuer den Preis-Service (Arbeitspaket 5).

Nutzt eine isolierte In-Memory-SQLite-Datenbank, um die reale app.db nicht
zu beruehren.
"""

import datetime as dt

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import Base
from src.db.models import MarketPrice, OtcSurcharge, PfcCheck, SettlementPrice
from src.services.price_service import (
    get_chat_text,
    get_mail_text,
    get_pfc_check_rows,
    get_price_table,
    save_prices_and_surcharges,
)

TODAY = dt.date(2026, 7, 4)
CURRENT_YEAR = TODAY.year
Y1, Y2, Y3 = CURRENT_YEAR + 1, CURRENT_YEAR + 2, CURRENT_YEAR + 3


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    with TestSession() as s:
        yield s


def _seed_full_price_set(session):
    now = dt.datetime(2026, 7, 4, 8, 0, 0)
    for product_type, year, price, surcharge, settlement in [
        ("Base", Y1, 85.00, 0.40, 84.80),
        ("Base", Y2, 79.50, 0.50, 79.10),
        ("Base", Y3, 76.20, 0.60, 75.90),
        ("Peak", Y1, 95.50, 0.65, 95.00),
        ("Peak", Y2, 89.30, 0.75, 88.90),
        ("Peak", Y3, 85.00, 0.85, 84.70),
    ]:
        session.add(MarketPrice(product_type=product_type, delivery_year=year, price_eur_mwh=price, price_timestamp=now))
        session.add(OtcSurcharge(product_type=product_type, delivery_year=year, surcharge_eur_mwh=surcharge))
        session.add(
            SettlementPrice(
                product_type=product_type,
                delivery_year=year,
                settlement_date=TODAY - dt.timedelta(days=1),
                settlement_price_eur_mwh=settlement,
                settlement_timestamp=now,
            )
        )
    session.add(
        PfcCheck(
            product_type="Base",
            delivery_year=Y1,
            pfc_mean_eur_mwh=85.10,
            pfc_file_timestamp=dt.datetime(2026, 7, 2, 0, 0, 0),
        )
    )
    session.commit()


def test_price_table_order_and_calculation(session):
    _seed_full_price_set(session)

    rows = get_price_table(session, today=TODAY)

    assert [row.label for row in rows] == [
        f"Base {Y1}", f"Base {Y2}", f"Base {Y3}", f"Peak {Y1}", f"Peak {Y2}", f"Peak {Y3}",
    ]
    base_y1 = rows[0]
    assert base_y1.market_price_eur_mwh == pytest.approx(85.00)
    assert base_y1.otc_surcharge_eur_mwh == pytest.approx(0.40)
    assert base_y1.final_price_eur_mwh == pytest.approx(85.40)
    assert base_y1.settlement_price_eur_mwh == pytest.approx(84.80)
    assert base_y1.difference_eur_mwh == pytest.approx(0.60)


def test_price_table_defaults_to_zero_when_missing(session):
    rows = get_price_table(session, today=TODAY)

    assert len(rows) == 6
    for row in rows:
        assert row.market_price_eur_mwh == 0.0
        assert row.otc_surcharge_eur_mwh == 0.0
        assert row.final_price_eur_mwh == 0.0
        assert row.settlement_price_eur_mwh is None
        assert row.difference_eur_mwh is None


def test_save_prices_and_surcharges_upserts(session):
    _seed_full_price_set(session)

    save_prices_and_surcharges(
        session,
        entries=[{"product_type": "Base", "delivery_year": Y1, "market_price_eur_mwh": 90.00, "otc_surcharge_eur_mwh": 1.00}],
    )

    rows = get_price_table(session, today=TODAY)
    base_y1 = next(r for r in rows if r.product_type == "Base" and r.delivery_year == Y1)
    assert base_y1.market_price_eur_mwh == pytest.approx(90.00)
    assert base_y1.otc_surcharge_eur_mwh == pytest.approx(1.00)
    assert base_y1.final_price_eur_mwh == pytest.approx(91.00)

    # Andere Produkte bleiben unveraendert.
    base_y2 = next(r for r in rows if r.product_type == "Base" and r.delivery_year == Y2)
    assert base_y2.market_price_eur_mwh == pytest.approx(79.50)


def test_pfc_check_rows_only_base_and_only_available_years(session):
    _seed_full_price_set(session)

    rows = get_pfc_check_rows(session, today=TODAY)

    # Nur Base Y1 wurde geseedet (Y2/Y3 fehlen -> keine harte Fehlermeldung, einfach weggelassen).
    assert len(rows) == 1
    assert rows[0].label == f"Base {Y1}"
    assert rows[0].pfc_mean_eur_mwh == pytest.approx(85.10)
    assert rows[0].settlement_price_eur_mwh == pytest.approx(84.80)
    assert rows[0].difference_eur_mwh == pytest.approx(0.30)


def test_chat_text_uses_text_order_and_no_difference(session):
    _seed_full_price_set(session)

    text = get_chat_text(session, today=TODAY)

    assert text.index(f"Base {Y1}") < text.index(f"Peak {Y1}") < text.index(f"Base {Y2}")
    assert "Differenz" not in text


def test_mail_text_includes_difference(session):
    _seed_full_price_set(session)

    text = get_mail_text(session, today=TODAY)

    assert "Differenz zum Settlement Vortag" in text
    assert f"Base {Y1}: 85,40 €/MWh (Differenz zum Settlement Vortag: +0,60 €/MWh)" in text
