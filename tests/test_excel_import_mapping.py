"""Tests fuer den Excel-/PFC-Mockdatenimport (Import-Arbeitspaket).

Nutzt die echte `data/mockdaten.xlsm` und `data/pfc/`-Dateien als Fixtures
sowie eine isolierte In-Memory-SQLite-Datenbank, um die reale app.db nicht
zu beruehren. `current_year`/`today` werden injiziert und bewusst auf 2026
gesetzt (die mitgelieferte Mockdatei ist auf Kalenderjahr 2026 zugeschnitten),
damit die Tests unabhaengig vom echten Systemdatum sind.
"""

import datetime as dt
from pathlib import Path

import openpyxl
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.database import Base
from src.db.models import (
    IntradayTrade,
    LimitOrder,
    MarketPrice,
    OtcSurcharge,
    PfcCheck,
    PortfolioPosition,
    SettlementPrice,
    TradingCalendarEntry,
)
from src.services.excel_import_service import (
    read_intraday_trades_from_excel,
    read_limit_orders_from_excel,
    read_market_prices_and_surcharges_from_excel,
    read_portfolio_positions_from_excel,
    read_settlement_prices_from_excel,
    read_trading_calendar_from_excel,
    seed_database_from_excel,
)
from src.services.pfc_import_service import read_pfc_checks_from_files

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
EXCEL_PATH = _PROJECT_ROOT / "data" / "mockdaten.xlsm"
PFC_DIR = _PROJECT_ROOT / "data" / "pfc"
CURRENT_YEAR = 2026
TODAY = dt.date(2026, 7, 5)


@pytest.fixture(scope="module")
def workbook():
    return openpyxl.load_workbook(EXCEL_PATH, data_only=True)


@pytest.fixture()
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestSession = sessionmaker(bind=engine)
    with TestSession() as s:
        yield s


def test_portfolio_positions_are_netted_v_minus_k(workbook):
    seeds, warnings = read_portfolio_positions_from_excel(workbook, CURRENT_YEAR)

    by_year = {s.year: s.position_mwh for s in seeds}
    assert by_year[2026] == pytest.approx(-11519.82, abs=0.01)
    assert by_year[2027] == pytest.approx(5675.33, abs=0.01)
    assert by_year[2028] == pytest.approx(-274.47, abs=0.01)
    assert by_year[2029] == pytest.approx(6923.93, abs=0.01)
    assert by_year[2030] == pytest.approx(0.0, abs=0.01)
    assert warnings == []


def test_intraday_trades_map_v_to_positive_and_k_to_negative(workbook):
    seeds, warnings = read_intraday_trades_from_excel(workbook, CURRENT_YEAR, TODAY)

    by_partner = {s.partner_alias: s for s in seeds}
    assert by_partner["Malermeister A"].quantity_y1_mwh == 5000.0
    assert by_partner["Malermeister A"].quantity_y3_mwh == 3000.0
    assert by_partner["Vattenfall"].quantity_y1_mwh == -8760.0
    assert by_partner["Vattenfall"].quantity_y3_mwh == -8760.0
    # Leeres Datum in Excel -> heutiges (injiziertes) Datum wird gesetzt.
    assert all(s.trade_date == TODAY for s in seeds)
    assert warnings == []


def test_market_prices_and_surcharges_cover_base_and_peak_y1_to_y3(workbook):
    prices, surcharges, warnings = read_market_prices_and_surcharges_from_excel(workbook, CURRENT_YEAR)

    price_by_key = {(p.product_type, p.delivery_year): p.price_eur_mwh for p in prices}
    assert price_by_key[("Base", 2027)] == pytest.approx(93.19)
    assert price_by_key[("Peak", 2029)] == pytest.approx(76.12)
    assert ("Base", 2030) not in price_by_key  # nur Y+1..Y+3 werden verwendet

    surcharge_by_key = {(s.product_type, s.delivery_year): s.surcharge_eur_mwh for s in surcharges}
    assert surcharge_by_key[("Base", 2027)] == pytest.approx(0.40)
    assert surcharge_by_key[("Peak", 2029)] == pytest.approx(0.85)
    assert warnings == []


def test_settlement_prices_use_excel_for_base_and_default_for_peak(workbook):
    seeds, warnings = read_settlement_prices_from_excel(workbook, CURRENT_YEAR)

    by_key = {(s.product_type, s.delivery_year): s for s in seeds}
    assert by_key[("Base", 2027)].settlement_price_eur_mwh == pytest.approx(92.98)
    assert by_key[("Base", 2027)].is_default is False
    assert by_key[("Peak", 2027)].is_default is True
    assert any("Peak-Settlementpreise" in w for w in warnings)


def test_trading_calendar_maps_kauf_to_positive_quantities(workbook):
    seeds, warnings = read_trading_calendar_from_excel(workbook, CURRENT_YEAR, TODAY)

    assert len(seeds) == 4
    holz = next(s for s in seeds if s.partner_alias == "Holz Gmbh")
    assert holz.direction == "partner_buys"
    assert holz.quantity_y1_mwh == pytest.approx(482.497)
    assert holz.quantity_y2_mwh == pytest.approx(317.898)
    assert holz.quantity_y0_mwh == 0.0
    assert holz.quantity_y4_mwh == 0.0
    assert warnings == []


def test_limit_orders_only_import_kauf_limit(workbook):
    seeds, warnings = read_limit_orders_from_excel(workbook, CURRENT_YEAR)

    assert len(seeds) == 2
    bau_ag = next(s for s in seeds if s.partner_alias == "Bau AG")
    assert bau_ag.trigger_product_type == "Base"
    assert bau_ag.trigger_delivery_year == 2027
    assert bau_ag.trigger_condition == "partner_buys_price_lt_limit"
    assert bau_ag.limit_price_eur_mwh == pytest.approx(90.0)
    assert bau_ag.quantity_y1_mwh == pytest.approx(8760.0)

    # Malermeister A: Peak 2028, gueltig-bis liegt bereits vor "heute" (TODAY)
    # - wird trotzdem als "offen" importiert (kein automatisches "abgelaufen",
    # siehe Modulkommentar / bestaetigter Klaerpunkt).
    malermeister = next(s for s in seeds if s.partner_alias == "Malermeister A")
    assert malermeister.trigger_product_type == "Peak"
    assert malermeister.quantity_y2_mwh == pytest.approx(200.0)
    assert malermeister.valid_until == dt.date(2026, 7, 3)


def test_pfc_checks_read_real_files_for_all_three_years():
    seeds, warnings = read_pfc_checks_from_files(PFC_DIR, CURRENT_YEAR, TODAY)

    assert len(seeds) == 3
    by_year = {s.delivery_year: s for s in seeds}
    assert by_year[2027].pfc_mean_eur_mwh == pytest.approx(92.98, abs=0.01)
    assert all(not s.is_default for s in seeds)
    assert warnings == []


def test_pfc_checks_fall_back_to_defaults_when_directory_missing(tmp_path):
    seeds, warnings = read_pfc_checks_from_files(tmp_path / "does_not_exist", CURRENT_YEAR, TODAY)

    assert len(seeds) == 3
    assert all(s.is_default for s in seeds)
    assert any("nicht gefunden" in w for w in warnings)


def test_seed_database_from_excel_populates_all_tables(session):
    report = seed_database_from_excel(session, excel_path=EXCEL_PATH, pfc_dir=PFC_DIR, today=TODAY)
    session.commit()

    assert report.already_seeded is False
    assert any("Peak-Settlementpreise" in w for w in report.warnings)
    assert session.query(PortfolioPosition).count() == 5
    assert session.query(IntradayTrade).count() == 2
    assert session.query(MarketPrice).count() == 6
    assert session.query(OtcSurcharge).count() == 6
    assert session.query(SettlementPrice).count() == 6
    assert session.query(TradingCalendarEntry).count() == 4
    assert session.query(LimitOrder).count() == 2
    assert session.query(PfcCheck).count() == 3


def test_seed_database_from_excel_does_not_overwrite_already_seeded_db(session):
    seed_database_from_excel(session, excel_path=EXCEL_PATH, pfc_dir=PFC_DIR, today=TODAY)
    session.commit()

    report_second_run = seed_database_from_excel(session, excel_path=EXCEL_PATH, pfc_dir=PFC_DIR, today=TODAY)

    assert report_second_run.already_seeded is True
    assert report_second_run.warnings == []
    # Kein doppelter Import durch den zweiten Lauf.
    assert session.query(PortfolioPosition).count() == 5
