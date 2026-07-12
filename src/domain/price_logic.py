"""Preisberechnung: finaler Preis und Settlement-Differenz.

Vorgabe: docs/specifications/01_fachliche_funktionen.md (Abschnitt 8.3).
Reine Funktionen ohne Streamlit-/DB-Abhaengigkeit.
"""


def final_price(market_price_eur_mwh: float, otc_surcharge_eur_mwh: float) -> float:
    """Finaler Preis = Marktpreis + OTC-Aufschlag."""
    return market_price_eur_mwh + otc_surcharge_eur_mwh


def settlement_difference(
    final_price_eur_mwh: float, settlement_price_eur_mwh: float | None
) -> float | None:
    """Differenz = Finaler Preis - Settlement Vortag.

    Liefert None, falls kein Settlementpreis vorliegt (reine Anzeigelogik,
    keine harte Fehlermeldung - siehe 01_fachliche_funktionen.md, Abschnitt 9.3).
    """
    if settlement_price_eur_mwh is None:
        return None
    return final_price_eur_mwh - settlement_price_eur_mwh
