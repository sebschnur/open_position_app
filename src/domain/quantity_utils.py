"""Mengen-, Vorzeichen- und Rundungslogik.

Vorgabe: docs/specifications/01_fachliche_funktionen.md (Abschnitt 6),
02_datenmodell_sqlite.md (Abschnitt 14/15). Reine Funktionen.

Zentrale Fachregel (Vorzeichenlogik):
- positive Menge = Partner kauft von uns  -> Positionswirkung positiv
- negative Menge = Partner verkauft an uns -> Positionswirkung negativ
"""

from typing import Iterable

from src.domain.calendar_utils import hours_in_year

INTERPRETATION_BUYS = "Partner kauft von uns"
INTERPRETATION_SELLS = "Partner verkauft an uns"
INTERPRETATION_NONE = "Keine Menge"
INTERPRETATION_MIXED = "Gemischte Vorzeichen - Jahresmengen pruefen"


def mwh_to_mw(quantity_mwh: float, year: int) -> float:
    """Rechnet eine Jahresliefermenge in MWh in eine Base-Leistung in MW um."""
    return quantity_mwh / hours_in_year(year)


def interpret_quantity(quantity_mwh: float) -> str:
    """Liefert die fachliche Interpretation einer einzelnen Menge anhand ihres Vorzeichens."""
    if quantity_mwh > 0:
        return INTERPRETATION_BUYS
    if quantity_mwh < 0:
        return INTERPRETATION_SELLS
    return INTERPRETATION_NONE


def interpret_quantities(quantities: Iterable[float]) -> str:
    """Interpretation ueber mehrere Jahresmengen eines Geschaefts hinweg.

    Ein Geschaeft kann Mengen fuer mehrere Lieferjahre enthalten. Haben alle
    befuellten (!= 0) Mengen dasselbe Vorzeichen, gilt die einheitliche
    Interpretation. Bei gemischten Vorzeichen waere eine einzelne
    Positionswirkung fachlich falsch (z. B. wuerde +5000 in einem Jahr und
    -5000 in einem anderen sich zu 0 aufsummieren und faelschlich als "Keine
    Menge" erscheinen) - das wird stattdessen explizit gekennzeichnet.
    """
    nonzero = [q for q in quantities if q != 0]
    if not nonzero:
        return INTERPRETATION_NONE
    has_positive = any(q > 0 for q in nonzero)
    has_negative = any(q < 0 for q in nonzero)
    if has_positive and has_negative:
        return INTERPRETATION_MIXED
    return INTERPRETATION_BUYS if has_positive else INTERPRETATION_SELLS


def round_price(value: float) -> float:
    """Preise in EUR/MWh: 2 Nachkommastellen."""
    return round(float(value), 2)


def round_mw(value: float) -> float:
    """Mengen in MW: 2 Nachkommastellen."""
    return round(float(value), 2)


def round_mwh(value: float) -> float:
    """Mengen in MWh: 0 Nachkommastellen."""
    return round(float(value), 0)
