"""Tests fuer Preisberechnung (Arbeitspaket 5)."""

import pytest

from src.domain.price_logic import final_price, settlement_difference


def test_final_price_is_market_plus_surcharge():
    assert final_price(85.00, 0.40) == pytest.approx(85.40)


def test_final_price_handles_negative_surcharge():
    assert final_price(85.00, -0.40) == pytest.approx(84.60)


def test_settlement_difference():
    assert settlement_difference(85.40, 84.80) == pytest.approx(0.60)


def test_settlement_difference_negative():
    assert settlement_difference(84.60, 85.00) == pytest.approx(-0.40)


def test_settlement_difference_none_when_no_settlement():
    assert settlement_difference(85.40, None) is None
