"""Repository fuer Marktpreise, OTC-Aufschlaege, Settlementpreise und PFC-Pruefung."""

import datetime as dt
from typing import Dict, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import MarketPrice, OtcSurcharge, PfcCheck, SettlementPrice


def get_market_prices_by_product_year(session: Session) -> Dict[Tuple[str, int], MarketPrice]:
    return {(row.product_type, row.delivery_year): row for row in session.scalars(select(MarketPrice))}


def get_otc_surcharges_by_product_year(session: Session) -> Dict[Tuple[str, int], OtcSurcharge]:
    return {(row.product_type, row.delivery_year): row for row in session.scalars(select(OtcSurcharge))}


def get_settlement_prices_by_product_year(session: Session) -> Dict[Tuple[str, int], SettlementPrice]:
    return {(row.product_type, row.delivery_year): row for row in session.scalars(select(SettlementPrice))}


def get_pfc_checks_by_year(session: Session) -> Dict[int, PfcCheck]:
    """Nur Base-Produkte relevant (PFC-Pruefung bezieht sich auf Base Y+1 bis Y+3)."""
    stmt = select(PfcCheck).where(PfcCheck.product_type == "Base")
    return {row.delivery_year: row for row in session.scalars(stmt)}


def upsert_market_price(
    session: Session,
    product_type: str,
    delivery_year: int,
    price_eur_mwh: float,
    price_timestamp: dt.datetime,
) -> MarketPrice:
    """Legt einen Marktpreis an oder aktualisiert ihn (unique je Produkt/Jahr)."""
    stmt = select(MarketPrice).where(
        MarketPrice.product_type == product_type, MarketPrice.delivery_year == delivery_year
    )
    existing = session.scalars(stmt).first()
    if existing is None:
        existing = MarketPrice(
            product_type=product_type,
            delivery_year=delivery_year,
            price_eur_mwh=price_eur_mwh,
            price_timestamp=price_timestamp,
        )
        session.add(existing)
    else:
        existing.price_eur_mwh = price_eur_mwh
        existing.price_timestamp = price_timestamp
    return existing


def upsert_otc_surcharge(
    session: Session,
    product_type: str,
    delivery_year: int,
    surcharge_eur_mwh: float,
) -> OtcSurcharge:
    """Legt einen OTC-Aufschlag an oder aktualisiert ihn (unique je Produkt/Jahr)."""
    stmt = select(OtcSurcharge).where(
        OtcSurcharge.product_type == product_type, OtcSurcharge.delivery_year == delivery_year
    )
    existing = session.scalars(stmt).first()
    if existing is None:
        existing = OtcSurcharge(
            product_type=product_type,
            delivery_year=delivery_year,
            surcharge_eur_mwh=surcharge_eur_mwh,
        )
        session.add(existing)
    else:
        existing.surcharge_eur_mwh = surcharge_eur_mwh
    return existing
