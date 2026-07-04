"""SQLAlchemy-Modelle fuer den Prototyp.

Bildet die Tabellen aus docs/specifications/02_datenmodell_sqlite.md ab.

Hinweis: Mengen- und Preisfelder werden pragmatisch als Float gespeichert
(SQLite kennt ohnehin keinen echten Decimal-Typ). Rundung fuer die Anzeige
(Preise 2, MWh 0, MW 2 Nachkommastellen) erfolgt in der Domain-Logik (AP3),
nicht beim Speichern.
"""

import datetime as dt
from typing import Optional

from sqlalchemy import Date, DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.database import Base


def _utcnow() -> dt.datetime:
    return dt.datetime.utcnow()


class PortfolioPosition(Base):
    """Mock-Position aus dem Portfoliomanagementsystem je Kalenderjahr."""

    __tablename__ = "portfolio_positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    as_of_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    position_mwh: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )


class IntradayTrade(Base):
    """Untertaegiges Geschaeft. Kein Richtungsfeld - Vorzeichen der Mengen ist massgeblich."""

    __tablename__ = "intraday_trades"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    trade_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    partner_alias: Mapped[str] = mapped_column(String(120), nullable=False)
    quantity_y0_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y1_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y2_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y3_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y4_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    source_type: Mapped[str] = mapped_column(String(30), nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)


class MarketPrice(Base):
    """Aktueller Marktpreis je Produkt (Base/Peak) und Lieferjahr."""

    __tablename__ = "market_prices"
    __table_args__ = (
        UniqueConstraint("product_type", "delivery_year", name="uq_market_prices_product_year"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_type: Mapped[str] = mapped_column(String(10), nullable=False)
    delivery_year: Mapped[int] = mapped_column(Integer, nullable=False)
    price_eur_mwh: Mapped[float] = mapped_column(Float, nullable=False)
    price_timestamp: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )


class OtcSurcharge(Base):
    """OTC-Aufschlag je Produkt (Base/Peak) und Lieferjahr."""

    __tablename__ = "otc_surcharges"
    __table_args__ = (
        UniqueConstraint("product_type", "delivery_year", name="uq_otc_surcharges_product_year"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_type: Mapped[str] = mapped_column(String(10), nullable=False)
    delivery_year: Mapped[int] = mapped_column(Integer, nullable=False)
    surcharge_eur_mwh: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )


class SettlementPrice(Base):
    """Settlementpreis des Vortages je Produkt (Base/Peak) und Lieferjahr."""

    __tablename__ = "settlement_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_type: Mapped[str] = mapped_column(String(10), nullable=False)
    delivery_year: Mapped[int] = mapped_column(Integer, nullable=False)
    settlement_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    settlement_price_eur_mwh: Mapped[float] = mapped_column(Float, nullable=False)
    settlement_timestamp: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )


class PfcCheck(Base):
    """PFC-Mittelwert und Zeitstempel fuer die PFC-Pruefung (nur Base Y+1 bis Y+3)."""

    __tablename__ = "pfc_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_type: Mapped[str] = mapped_column(String(10), nullable=False)
    delivery_year: Mapped[int] = mapped_column(Integer, nullable=False)
    pfc_mean_eur_mwh: Mapped[float] = mapped_column(Float, nullable=False)
    pfc_file_timestamp: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )


class LimitOrder(Base):
    """Limitorder mit Trigger-Preis, Ausloesebedingung und Status."""

    __tablename__ = "limit_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    partner_alias: Mapped[str] = mapped_column(String(120), nullable=False)
    quantity_y0_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y1_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y2_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y3_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y4_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    trigger_product_type: Mapped[str] = mapped_column(String(10), nullable=False)
    trigger_delivery_year: Mapped[int] = mapped_column(Integer, nullable=False)
    trigger_condition: Mapped[str] = mapped_column(String(40), nullable=False)
    limit_price_eur_mwh: Mapped[float] = mapped_column(Float, nullable=False)
    responsible_trading: Mapped[str] = mapped_column(String(120), nullable=False)
    responsible_sales: Mapped[str] = mapped_column(String(120), nullable=False)
    valid_until: Mapped[Optional[dt.date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="offen")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )


class TradingCalendarEntry(Base):
    """Handelskalendereintrag mit Richtung, Mengen und Status."""

    __tablename__ = "trading_calendar"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    due_date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    partner_alias: Mapped[str] = mapped_column(String(120), nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)
    quantity_y0_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y1_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y2_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y3_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    quantity_y4_mwh: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="geplant")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=_utcnow, nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )


class AppMetadata(Base):
    """Technische Metadaten, z. B. Initialisierungsstatus."""

    __tablename__ = "app_metadata"

    key: Mapped[str] = mapped_column(String(80), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )
