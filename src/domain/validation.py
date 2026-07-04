"""Fachliche Validierungen fuer Mengen und Vorzeichen.

Vorgabe: docs/specifications/02_datenmodell_sqlite.md (Abschnitt 15),
03_streamlit_ui_konzept.md (Abschnitt 6.5/7.6). Reine Funktionen.

Konvention:
- "positive" = Partner kauft von uns  -> alle befuellten Mengen muessen > 0 sein
- "negative" = Partner verkauft an uns -> alle befuellten Mengen muessen < 0 sein
"""

from typing import Iterable

from src.domain.limit_order_logic import (
    TRIGGER_PARTNER_BUYS_GT,
    TRIGGER_PARTNER_BUYS_LT,
    TRIGGER_PARTNER_SELLS_GT,
    TRIGGER_PARTNER_SELLS_LT,
)

SIGN_POSITIVE = "positive"
SIGN_NEGATIVE = "negative"

DIRECTION_PARTNER_BUYS = "partner_buys"
DIRECTION_PARTNER_SELLS = "partner_sells"

_TRIGGER_CONDITION_SIGN = {
    TRIGGER_PARTNER_BUYS_GT: SIGN_POSITIVE,
    TRIGGER_PARTNER_BUYS_LT: SIGN_POSITIVE,
    TRIGGER_PARTNER_SELLS_GT: SIGN_NEGATIVE,
    TRIGGER_PARTNER_SELLS_LT: SIGN_NEGATIVE,
}

_DIRECTION_SIGN = {
    DIRECTION_PARTNER_BUYS: SIGN_POSITIVE,
    DIRECTION_PARTNER_SELLS: SIGN_NEGATIVE,
}


def expected_sign_for_trigger_condition(trigger_condition: str) -> str:
    """Erwartetes Mengenvorzeichen fuer eine Limitorder-Ausloeseart."""
    try:
        return _TRIGGER_CONDITION_SIGN[trigger_condition]
    except KeyError:
        raise ValueError(f"Unbekannte Ausloeseart: {trigger_condition!r}") from None


def expected_sign_for_direction(direction: str) -> str:
    """Erwartetes Mengenvorzeichen fuer eine Handelskalender-Richtung."""
    try:
        return _DIRECTION_SIGN[direction]
    except KeyError:
        raise ValueError(f"Unbekannte Richtung: {direction!r}") from None


def at_least_one_nonzero(quantities: Iterable[float]) -> bool:
    """Mindestens ein Lieferjahr muss eine Menge ungleich 0 haben."""
    return any(q != 0 for q in quantities)


def all_nonzero_match_sign(quantities: Iterable[float], expected_sign: str) -> bool:
    """Alle befuellten (!= 0) Mengen muessen zum erwarteten Vorzeichen passen."""
    for q in quantities:
        if q == 0:
            continue
        if expected_sign == SIGN_POSITIVE and q < 0:
            return False
        if expected_sign == SIGN_NEGATIVE and q > 0:
            return False
    return True


def validate_trade_quantities(quantities: Iterable[float], expected_sign: str) -> list[str]:
    """Prueft Mengen gegen das erwartete Vorzeichen.

    Gibt eine Liste von Fehlermeldungen zurueck (leer = gueltig), damit die UI
    alle Verstoesse gemeinsam anzeigen kann.
    """
    quantities = list(quantities)
    errors: list[str] = []

    if not at_least_one_nonzero(quantities):
        errors.append("Mindestens ein Lieferjahr muss eine Menge ungleich 0 haben.")

    if not all_nonzero_match_sign(quantities, expected_sign):
        if expected_sign == SIGN_POSITIVE:
            errors.append("Partner kauft: alle befuellten Mengen muessen positiv sein.")
        else:
            errors.append("Partner verkauft: alle befuellten Mengen muessen negativ sein.")

    return errors
