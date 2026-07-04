"""Erzeugt plausible Default-Mockdaten fuer eine leere Datenbank.

Diese Daten sind NICHT aus der Excel-Mockdatei abgeleitet - das uebernimmt
das spaetere Import-Arbeitspaket (docs/specifications/06_excel_mockdaten_import.md).
Sie sorgen nur dafuer, dass die App direkt nach der Initialisierung fachlich
plausibel benutzbar ist.
"""

import datetime as dt

from sqlalchemy.orm import Session

from src.config import PRICE_PRODUCT_ORDER_TABLE
from src.db.models import (
    AppMetadata,
    IntradayTrade,
    LimitOrder,
    MarketPrice,
    OtcSurcharge,
    PfcCheck,
    PortfolioPosition,
    SettlementPrice,
    TradingCalendarEntry,
)

SOURCE_LABEL = "default_mock"

_BASE_MARKET_PRICE = {1: 85.00, 2: 79.50, 3: 76.20}
_PEAK_MARKET_PRICE = {1: 95.50, 2: 89.30, 3: 85.00}
_BASE_OTC_SURCHARGE = {1: 0.40, 2: 0.50, 3: 0.60}
_PEAK_OTC_SURCHARGE = {1: 0.65, 2: 0.75, 3: 0.85}
_BASE_SETTLEMENT_PRICE = {1: 84.80, 2: 79.10, 3: 75.90}
_PEAK_SETTLEMENT_PRICE = {1: 95.00, 2: 88.90, 3: 84.70}
_BASE_PFC_MEAN = {1: 85.10, 2: 79.60, 3: 76.30}

# Y0 (aktuelles Jahr) bis Y+4: plausible Netto-Positionen in MWh.
_PORTFOLIO_POSITION_BY_OFFSET = {0: 15000.0, 1: -8000.0, 2: 4000.0, 3: -2000.0, 4: 0.0}


def _offset_from_label(label: str) -> int:
    return int(label.replace("Y+", ""))


def seed_default_mock_data(session: Session) -> None:
    """Befuellt eine leere Datenbank mit Default-Mockdaten fuer alle Fachtabellen."""
    today = dt.date.today()
    now = dt.datetime.utcnow()
    current_year = today.year

    _seed_portfolio_positions(session, current_year, today)
    _seed_intraday_trades(session, today)
    _seed_prices_and_surcharges(session, current_year, now)
    _seed_settlement_prices(session, current_year, today, now)
    _seed_pfc_checks(session, current_year, today)
    _seed_limit_orders(session, current_year, today)
    _seed_trading_calendar(session, today)
    _upsert_metadata(session, "db_initialized", "true", now)
    _upsert_metadata(session, "initial_seed_source", SOURCE_LABEL, now)


def _seed_portfolio_positions(session: Session, current_year: int, today: dt.date) -> None:
    for offset, position_mwh in _PORTFOLIO_POSITION_BY_OFFSET.items():
        session.add(
            PortfolioPosition(
                as_of_date=today,
                year=current_year + offset,
                position_mwh=position_mwh,
                source=SOURCE_LABEL,
            )
        )


def _seed_intraday_trades(session: Session, today: dt.date) -> None:
    session.add(
        IntradayTrade(
            trade_date=today,
            partner_alias="Muster Partner A",
            quantity_y1_mwh=2500.0,
            source_type="manual",
        )
    )
    session.add(
        IntradayTrade(
            trade_date=today,
            partner_alias="Muster Partner B",
            quantity_y1_mwh=-1200.0,
            source_type="manual",
        )
    )


def _seed_prices_and_surcharges(session: Session, current_year: int, now: dt.datetime) -> None:
    for product_type, year_label in PRICE_PRODUCT_ORDER_TABLE:
        offset = _offset_from_label(year_label)
        delivery_year = current_year + offset
        price = (_BASE_MARKET_PRICE if product_type == "Base" else _PEAK_MARKET_PRICE)[offset]
        surcharge = (_BASE_OTC_SURCHARGE if product_type == "Base" else _PEAK_OTC_SURCHARGE)[offset]
        session.add(
            MarketPrice(
                product_type=product_type,
                delivery_year=delivery_year,
                price_eur_mwh=price,
                price_timestamp=now,
            )
        )
        session.add(
            OtcSurcharge(
                product_type=product_type,
                delivery_year=delivery_year,
                surcharge_eur_mwh=surcharge,
            )
        )


def _seed_settlement_prices(
    session: Session, current_year: int, today: dt.date, now: dt.datetime
) -> None:
    settlement_date = today - dt.timedelta(days=1)
    for product_type, year_label in PRICE_PRODUCT_ORDER_TABLE:
        offset = _offset_from_label(year_label)
        delivery_year = current_year + offset
        price = (
            _BASE_SETTLEMENT_PRICE if product_type == "Base" else _PEAK_SETTLEMENT_PRICE
        )[offset]
        session.add(
            SettlementPrice(
                product_type=product_type,
                delivery_year=delivery_year,
                settlement_date=settlement_date,
                settlement_price_eur_mwh=price,
                settlement_timestamp=now,
            )
        )


def _seed_pfc_checks(session: Session, current_year: int, today: dt.date) -> None:
    # PFC-Pruefung bezieht sich im Prototyp nur auf Base Y+1 bis Y+3.
    pfc_timestamp = dt.datetime.combine(today, dt.time.min)
    for offset, mean_value in _BASE_PFC_MEAN.items():
        session.add(
            PfcCheck(
                product_type="Base",
                delivery_year=current_year + offset,
                pfc_mean_eur_mwh=mean_value,
                pfc_file_timestamp=pfc_timestamp,
            )
        )


def _seed_limit_orders(session: Session, current_year: int, today: dt.date) -> None:
    # Mock-Fall gemaess 06_excel_mockdaten_import.md: nur "Partner kauft, wenn
    # Preis <= Limit", technisch als "partner_buys_price_lt_limit" abgebildet.
    session.add(
        LimitOrder(
            partner_alias="Muster Kunde C",
            quantity_y1_mwh=8760.0,
            trigger_product_type="Base",
            trigger_delivery_year=current_year + 1,
            trigger_condition="partner_buys_price_lt_limit",
            limit_price_eur_mwh=90.00,
            responsible_trading="Handel Mustermann",
            responsible_sales="Vertrieb Musterfrau",
            valid_until=today + dt.timedelta(days=90),
            status="offen",
        )
    )


def _seed_trading_calendar(session: Session, today: dt.date) -> None:
    session.add(
        TradingCalendarEntry(
            due_date=today + dt.timedelta(days=7),
            partner_alias="Muster Kunde D",
            direction="partner_buys",
            quantity_y1_mwh=5000.0,
            status="geplant",
        )
    )
    session.add(
        TradingCalendarEntry(
            due_date=today - dt.timedelta(days=3),
            partner_alias="Muster Kunde E",
            direction="partner_sells",
            quantity_y1_mwh=-3000.0,
            status="geplant",
        )
    )


def _upsert_metadata(session: Session, key: str, value: str, now: dt.datetime) -> None:
    entry = session.get(AppMetadata, key)
    if entry is None:
        session.add(AppMetadata(key=key, value=value, updated_at=now))
    else:
        entry.value = value
        entry.updated_at = now
