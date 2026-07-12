"""Limitorder-Triggerlogik.

Vorgabe: docs/specifications/01_fachliche_funktionen.md (Abschnitt 11),
04_workflows_automatisierungen.md (Abschnitt 10),
02_datenmodell_sqlite.md (Abschnitt 11.1). Reine Funktionen.

Die Triggerbedingung entscheidet nur ueber den Preisvergleich (> oder < Limit).
Die Richtung (kauft/verkauft) bestimmt NICHT den Vergleich, sondern nur das
erwartete Mengenvorzeichen (siehe validation.py). Es gibt keine automatische
Ausfuehrung - die Funktion markiert lediglich, ob die Bedingung erfuellt ist.
"""

# Technische Werte gemaess 02_datenmodell_sqlite.md, Abschnitt 11.1.
TRIGGER_PARTNER_BUYS_GT = "partner_buys_price_gt_limit"
TRIGGER_PARTNER_BUYS_LT = "partner_buys_price_lt_limit"
TRIGGER_PARTNER_SELLS_GT = "partner_sells_price_gt_limit"
TRIGGER_PARTNER_SELLS_LT = "partner_sells_price_lt_limit"

# UI-Texte je technischem Wert.
TRIGGER_CONDITION_LABELS = {
    TRIGGER_PARTNER_BUYS_GT: "Partner kauft, wenn Marktpreis > Limit",
    TRIGGER_PARTNER_BUYS_LT: "Partner kauft, wenn Marktpreis < Limit",
    TRIGGER_PARTNER_SELLS_GT: "Partner verkauft, wenn Marktpreis > Limit",
    TRIGGER_PARTNER_SELLS_LT: "Partner verkauft, wenn Marktpreis < Limit",
}

_GREATER_THAN_CONDITIONS = {TRIGGER_PARTNER_BUYS_GT, TRIGGER_PARTNER_SELLS_GT}
_LESS_THAN_CONDITIONS = {TRIGGER_PARTNER_BUYS_LT, TRIGGER_PARTNER_SELLS_LT}


def is_triggered(
    trigger_condition: str, market_price: float, limit_price: float
) -> bool:
    """Prueft, ob die Ausloesebedingung gegen den aktuellen Marktpreis erfuellt ist."""
    if trigger_condition in _GREATER_THAN_CONDITIONS:
        return market_price > limit_price
    if trigger_condition in _LESS_THAN_CONDITIONS:
        return market_price < limit_price
    raise ValueError(f"Unbekannte Ausloeseart: {trigger_condition!r}")
