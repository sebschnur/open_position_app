"""Position-Service: aggregiert PMS-Position und untertaegige Geschaefte je Jahr.

Vorgabe: docs/specifications/01_fachliche_funktionen.md (Abschnitt 5),
04_workflows_automatisierungen.md (Abschnitt 3).

Es gibt kein Richtungsfeld bei untertaegigen Geschaeften. Die einzige
Eingabe-Validierung ist "mindestens eine Menge != 0" - eine Vorzeichenregel
gibt es hier bewusst nicht (siehe 01_fachliche_funktionen.md, Abschnitt 6.2).
"""

import datetime as dt
from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.orm import Session

from src.config import POSITION_LIMIT_MW
from src.domain.position_logic import limit_status, simulated_position_mw, utilization_pct
from src.domain.quantity_utils import interpret_quantities, mwh_to_mw, round_mw, round_mwh
from src.domain.validation import at_least_one_nonzero
from src.repositories.intraday_trade_repository import (
    add_intraday_trade as _repo_add_intraday_trade,
)
from src.repositories.intraday_trade_repository import (
    delete_intraday_trade as _repo_delete_intraday_trade,
)
from src.repositories.intraday_trade_repository import list_intraday_trades
from src.repositories.portfolio_repository import get_portfolio_positions_by_year

# Offsets fuer Y0 (aktuelles Jahr) bis Y+4.
YEAR_OFFSETS = range(5)


@dataclass
class PositionRow:
    year: int
    pms_position_mw: float
    intraday_position_mw: float
    simulated_position_mw: float
    limit_mw: float
    utilization_pct: float
    status: str


@dataclass
class IntradayTradeRow:
    id: int
    trade_date: dt.date
    partner_alias: str
    quantity_y0_mwh: float
    quantity_y1_mwh: float
    quantity_y2_mwh: float
    quantity_y3_mwh: float
    quantity_y4_mwh: float
    interpretation: str
    source_type: str
    last_modified_by: str


def get_position_table(session: Session, today: Optional[dt.date] = None) -> List[PositionRow]:
    """Berechnet die Positionstabelle fuer Y0 bis Y+4 (aktuelles Jahr automatisch bestimmt)."""
    today = today or dt.date.today()
    current_year = today.year
    years = [current_year + offset for offset in YEAR_OFFSETS]

    pms_by_year = get_portfolio_positions_by_year(session, years)
    intraday_sum_by_offset = _sum_intraday_quantities_by_offset(session)

    rows = []
    for offset, year in zip(YEAR_OFFSETS, years):
        pms_mw = mwh_to_mw(pms_by_year.get(year, 0.0), year)
        intraday_mw = mwh_to_mw(intraday_sum_by_offset[offset], year)
        simulated_mw = simulated_position_mw(pms_mw, intraday_mw)

        rows.append(
            PositionRow(
                year=year,
                pms_position_mw=round_mw(pms_mw),
                intraday_position_mw=round_mw(intraday_mw),
                simulated_position_mw=round_mw(simulated_mw),
                limit_mw=POSITION_LIMIT_MW,
                utilization_pct=round(utilization_pct(simulated_mw), 1),
                status=limit_status(simulated_mw),
            )
        )
    return rows


def _sum_intraday_quantities_by_offset(session: Session) -> dict:
    totals = {offset: 0.0 for offset in YEAR_OFFSETS}
    for trade in list_intraday_trades(session):
        totals[0] += trade.quantity_y0_mwh
        totals[1] += trade.quantity_y1_mwh
        totals[2] += trade.quantity_y2_mwh
        totals[3] += trade.quantity_y3_mwh
        totals[4] += trade.quantity_y4_mwh
    return totals


def get_intraday_trade_rows(session: Session) -> List[IntradayTradeRow]:
    """Liefert alle untertaegigen Geschaefte inkl. Interpretation fuer die Anzeige.

    Die Interpretation wird ueber alle fuenf Jahresmengen hinweg gebildet
    (nicht aus deren Summe, siehe interpret_quantities), damit gegenlaeufige
    Vorzeichen sich nicht faelschlich zu "Keine Menge" aufheben.
    """
    rows = []
    for trade in list_intraday_trades(session):
        quantities = [
            trade.quantity_y0_mwh,
            trade.quantity_y1_mwh,
            trade.quantity_y2_mwh,
            trade.quantity_y3_mwh,
            trade.quantity_y4_mwh,
        ]
        rows.append(
            IntradayTradeRow(
                id=trade.id,
                trade_date=trade.trade_date,
                partner_alias=trade.partner_alias,
                quantity_y0_mwh=round_mwh(trade.quantity_y0_mwh),
                quantity_y1_mwh=round_mwh(trade.quantity_y1_mwh),
                quantity_y2_mwh=round_mwh(trade.quantity_y2_mwh),
                quantity_y3_mwh=round_mwh(trade.quantity_y3_mwh),
                quantity_y4_mwh=round_mwh(trade.quantity_y4_mwh),
                interpretation=interpret_quantities(quantities),
                source_type=trade.source_type,
                last_modified_by=trade.last_modified_by,
            )
        )
    return rows


def add_intraday_trade(
    session: Session,
    trade_date: dt.date,
    partner_alias: str,
    quantity_y0_mwh: float,
    quantity_y1_mwh: float,
    quantity_y2_mwh: float,
    quantity_y3_mwh: float,
    quantity_y4_mwh: float,
    username: str = "system",
    source_type: str = "manual",
    source_id: Optional[int] = None,
) -> List[str]:
    """Validiert und speichert ein neues untertaegiges Geschaeft.

    ``username`` wird als letzter Bearbeiter gespeichert (Nachvollziehbarkeit).
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
    if not at_least_one_nonzero(quantities):
        return ["Mindestens ein Lieferjahr muss eine Menge ungleich 0 haben."]

    _repo_add_intraday_trade(
        session,
        trade_date=trade_date,
        partner_alias=partner_alias,
        quantity_y0_mwh=quantities[0],
        quantity_y1_mwh=quantities[1],
        quantity_y2_mwh=quantities[2],
        quantity_y3_mwh=quantities[3],
        quantity_y4_mwh=quantities[4],
        source_type=source_type,
        source_id=source_id,
        last_modified_by=username,
    )
    session.commit()
    return []


def delete_intraday_trade(session: Session, trade_id: int) -> None:
    """Loescht ein untertaegiges Geschaeft und committet die Aenderung."""
    _repo_delete_intraday_trade(session, trade_id)
    session.commit()
