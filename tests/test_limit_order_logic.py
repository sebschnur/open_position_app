"""Tests fuer Limitorder-Triggerlogik (Arbeitspaket 3/6)."""

import pytest

from src.domain.limit_order_logic import (
    TRIGGER_PARTNER_BUYS_GT,
    TRIGGER_PARTNER_BUYS_LT,
    TRIGGER_PARTNER_SELLS_GT,
    TRIGGER_PARTNER_SELLS_LT,
    is_triggered,
)


@pytest.mark.parametrize(
    "condition, market_price, limit_price, expected",
    [
        # "> Limit"-Bedingungen
        (TRIGGER_PARTNER_BUYS_GT, 95.0, 90.0, True),
        (TRIGGER_PARTNER_BUYS_GT, 85.0, 90.0, False),
        (TRIGGER_PARTNER_SELLS_GT, 95.0, 90.0, True),
        (TRIGGER_PARTNER_SELLS_GT, 85.0, 90.0, False),
        # "< Limit"-Bedingungen
        (TRIGGER_PARTNER_BUYS_LT, 85.0, 90.0, True),
        (TRIGGER_PARTNER_BUYS_LT, 95.0, 90.0, False),
        (TRIGGER_PARTNER_SELLS_LT, 85.0, 90.0, True),
        (TRIGGER_PARTNER_SELLS_LT, 95.0, 90.0, False),
    ],
)
def test_is_triggered(condition, market_price, limit_price, expected):
    assert is_triggered(condition, market_price, limit_price) is expected


def test_exact_match_does_not_trigger():
    # Preis exakt am Limit loest weder ">"- noch "<"-Bedingung aus.
    assert is_triggered(TRIGGER_PARTNER_BUYS_GT, 90.0, 90.0) is False
    assert is_triggered(TRIGGER_PARTNER_BUYS_LT, 90.0, 90.0) is False


def test_unknown_condition_raises():
    with pytest.raises(ValueError):
        is_triggered("unbekannt", 90.0, 90.0)
