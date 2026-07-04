"""Preis-Service: Marktpreise, OTC-Aufschlaege, Settlement-Vergleich, Texte und PFC-Anzeige.

Vorgabe: docs/specifications/01_fachliche_funktionen.md (Abschnitt 8-10),
04_workflows_automatisierungen.md (Abschnitt 6-9).
"""

import datetime as dt
from dataclasses import dataclass
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from src.config import PRICE_PRODUCT_ORDER_TABLE, PRICE_PRODUCT_ORDER_TEXT
from src.domain.price_logic import final_price, settlement_difference
from src.domain.quantity_utils import round_price
from src.domain.text_generation import PriceTextEntry, build_chat_text, build_mail_text
from src.repositories.price_repository import (
    get_market_prices_by_product_year,
    get_otc_surcharges_by_product_year,
    get_pfc_checks_by_year,
    get_settlement_prices_by_product_year,
    upsert_market_price,
    upsert_otc_surcharge,
)

# PFC-Pruefung bezieht sich im Prototyp nur auf Base Y+1 bis Y+3.
PFC_YEAR_OFFSETS = (1, 2, 3)


@dataclass
class PriceRow:
    product_type: str
    delivery_year: int
    label: str
    market_price_eur_mwh: float
    otc_surcharge_eur_mwh: float
    final_price_eur_mwh: float
    settlement_price_eur_mwh: Optional[float]
    difference_eur_mwh: Optional[float]


@dataclass
class PfcCheckRow:
    delivery_year: int
    label: str
    pfc_mean_eur_mwh: float
    settlement_price_eur_mwh: Optional[float]
    difference_eur_mwh: Optional[float]
    pfc_file_timestamp: dt.datetime
    settlement_timestamp: Optional[dt.datetime]


def _offset_from_label(label: str) -> int:
    return int(label.replace("Y+", ""))


def _product_label(product_type: str, delivery_year: int) -> str:
    return f"{product_type} {delivery_year}"


def get_price_table(session: Session, today: Optional[dt.date] = None) -> List[PriceRow]:
    """Liefert die Preistabelle in der Anzeige-Reihenfolge (Base Y+1..Y+3, Peak Y+1..Y+3)."""
    today = today or dt.date.today()
    current_year = today.year

    market_prices = get_market_prices_by_product_year(session)
    surcharges = get_otc_surcharges_by_product_year(session)
    settlements = get_settlement_prices_by_product_year(session)

    rows = []
    for product_type, year_label in PRICE_PRODUCT_ORDER_TABLE:
        delivery_year = current_year + _offset_from_label(year_label)
        key = (product_type, delivery_year)

        market_price_entry = market_prices.get(key)
        surcharge_entry = surcharges.get(key)
        settlement_entry = settlements.get(key)

        market_price_value = round_price(market_price_entry.price_eur_mwh if market_price_entry else 0.0)
        surcharge_value = round_price(surcharge_entry.surcharge_eur_mwh if surcharge_entry else 0.0)
        final_price_value = round_price(final_price(market_price_value, surcharge_value))
        settlement_value = (
            round_price(settlement_entry.settlement_price_eur_mwh) if settlement_entry else None
        )
        difference_value = settlement_difference(final_price_value, settlement_value)
        if difference_value is not None:
            difference_value = round_price(difference_value)

        rows.append(
            PriceRow(
                product_type=product_type,
                delivery_year=delivery_year,
                label=_product_label(product_type, delivery_year),
                market_price_eur_mwh=market_price_value,
                otc_surcharge_eur_mwh=surcharge_value,
                final_price_eur_mwh=final_price_value,
                settlement_price_eur_mwh=settlement_value,
                difference_eur_mwh=difference_value,
            )
        )
    return rows


def save_prices_and_surcharges(
    session: Session,
    entries: List[Dict],
    now: Optional[dt.datetime] = None,
) -> None:
    """Speichert Marktpreise und OTC-Aufschlaege gemeinsam - kein getrennter Speichern-Button.

    entries: Liste von Dicts mit den Schluesseln "product_type", "delivery_year",
    "market_price_eur_mwh", "otc_surcharge_eur_mwh".
    """
    now = now or dt.datetime.utcnow()
    for entry in entries:
        upsert_market_price(
            session,
            product_type=entry["product_type"],
            delivery_year=entry["delivery_year"],
            price_eur_mwh=entry["market_price_eur_mwh"],
            price_timestamp=now,
        )
        upsert_otc_surcharge(
            session,
            product_type=entry["product_type"],
            delivery_year=entry["delivery_year"],
            surcharge_eur_mwh=entry["otc_surcharge_eur_mwh"],
        )
    session.commit()


def get_pfc_check_rows(session: Session, today: Optional[dt.date] = None) -> List[PfcCheckRow]:
    """PFC-Pruefung bezieht sich im Prototyp nur auf Base Y+1 bis Y+3."""
    today = today or dt.date.today()
    current_year = today.year

    pfc_checks = get_pfc_checks_by_year(session)
    settlements = get_settlement_prices_by_product_year(session)

    rows = []
    for offset in PFC_YEAR_OFFSETS:
        delivery_year = current_year + offset
        pfc_entry = pfc_checks.get(delivery_year)
        if pfc_entry is None:
            continue  # reine Anzeige - keine Fehlermeldung, wenn (noch) keine PFC-Daten vorliegen

        settlement_entry = settlements.get(("Base", delivery_year))
        settlement_value = (
            round_price(settlement_entry.settlement_price_eur_mwh) if settlement_entry else None
        )
        pfc_value = round_price(pfc_entry.pfc_mean_eur_mwh)
        difference_value = settlement_difference(pfc_value, settlement_value)
        if difference_value is not None:
            difference_value = round_price(difference_value)

        rows.append(
            PfcCheckRow(
                delivery_year=delivery_year,
                label=_product_label("Base", delivery_year),
                pfc_mean_eur_mwh=pfc_value,
                settlement_price_eur_mwh=settlement_value,
                difference_eur_mwh=difference_value,
                pfc_file_timestamp=pfc_entry.pfc_file_timestamp,
                settlement_timestamp=settlement_entry.settlement_timestamp if settlement_entry else None,
            )
        )
    return rows


def _text_entries(session: Session, today: Optional[dt.date], with_difference: bool) -> List[PriceTextEntry]:
    today = today or dt.date.today()
    current_year = today.year

    market_prices = get_market_prices_by_product_year(session)
    surcharges = get_otc_surcharges_by_product_year(session)
    settlements = get_settlement_prices_by_product_year(session) if with_difference else {}

    entries = []
    for product_type, year_label in PRICE_PRODUCT_ORDER_TEXT:
        delivery_year = current_year + _offset_from_label(year_label)
        key = (product_type, delivery_year)

        market_price_entry = market_prices.get(key)
        surcharge_entry = surcharges.get(key)
        market_price_value = round_price(market_price_entry.price_eur_mwh if market_price_entry else 0.0)
        surcharge_value = round_price(surcharge_entry.surcharge_eur_mwh if surcharge_entry else 0.0)
        final_price_value = round_price(final_price(market_price_value, surcharge_value))

        difference_value = None
        if with_difference:
            settlement_entry = settlements.get(key)
            if settlement_entry is not None:
                settlement_value = round_price(settlement_entry.settlement_price_eur_mwh)
                difference_value = round_price(settlement_difference(final_price_value, settlement_value))

        entries.append(
            PriceTextEntry(
                label=_product_label(product_type, delivery_year),
                final_price_eur_mwh=final_price_value,
                difference_eur_mwh=difference_value,
            )
        )
    return entries


def get_chat_text(session: Session, today: Optional[dt.date] = None) -> str:
    """Chat-Kurztext: finale Preise in Chat-Reihenfolge, ohne Settlement-Differenz."""
    entries = _text_entries(session, today, with_difference=False)
    return build_chat_text(entries)


def get_mail_text(session: Session, today: Optional[dt.date] = None) -> str:
    """Mailtext: finale Preise in Chat-Reihenfolge, inkl. Differenz zum Settlement Vortag."""
    entries = _text_entries(session, today, with_difference=True)
    return build_mail_text(entries)
