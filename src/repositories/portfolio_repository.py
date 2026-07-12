"""Repository fuer portfolio_positions."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.db.models import PortfolioPosition


def get_portfolio_positions_by_year(session: Session, years: list[int]) -> dict:
    """Liefert die Netto-PMS-Position in MWh je Jahr (0.0, falls keine Daten vorhanden)."""
    stmt = select(PortfolioPosition).where(PortfolioPosition.year.in_(years))
    totals = {year: 0.0 for year in years}
    for row in session.scalars(stmt):
        totals[row.year] = totals.get(row.year, 0.0) + row.position_mwh
    return totals
