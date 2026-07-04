"""Tests fuer Mengen-, Vorzeichen- und Rundungslogik (Arbeitspaket 3)."""

import pytest

from src.domain.quantity_utils import (
    INTERPRETATION_BUYS,
    INTERPRETATION_MIXED,
    INTERPRETATION_NONE,
    INTERPRETATION_SELLS,
    interpret_quantities,
    interpret_quantity,
    mwh_to_mw,
    round_mw,
    round_mwh,
    round_price,
)


def test_mwh_to_mw_normal_year():
    # 8760 MWh in einem normalen Jahr entsprechen exakt 1 MW Base.
    assert mwh_to_mw(8760, 2025) == pytest.approx(1.0)


def test_mwh_to_mw_leap_year():
    # 8784 MWh in einem Schaltjahr entsprechen exakt 1 MW Base.
    assert mwh_to_mw(8784, 2024) == pytest.approx(1.0)


def test_mwh_to_mw_negative_keeps_sign():
    assert mwh_to_mw(-8760, 2025) == pytest.approx(-1.0)


@pytest.mark.parametrize(
    "quantity, expected",
    [
        (5000, INTERPRETATION_BUYS),
        (-5000, INTERPRETATION_SELLS),
        (0, INTERPRETATION_NONE),
    ],
)
def test_interpret_quantity(quantity, expected):
    assert interpret_quantity(quantity) == expected


@pytest.mark.parametrize(
    "quantities, expected",
    [
        ([0, 5000, 0, 3000, 0], INTERPRETATION_BUYS),
        ([0, -5000, 0, -3000, 0], INTERPRETATION_SELLS),
        ([0, 0, 0, 0, 0], INTERPRETATION_NONE),
        # Regressionsfall: +5000 in Y1 und -5000 in Y2 duerfen sich NICHT zu
        # "Keine Menge" aufheben - beide Jahre haben echte Positionswirkung.
        ([0, 5000, -5000, 0, 0], INTERPRETATION_MIXED),
        ([0, 8760, -100, 0, 0], INTERPRETATION_MIXED),
    ],
)
def test_interpret_quantities_across_years(quantities, expected):
    assert interpret_quantities(quantities) == expected


def test_round_price_two_decimals():
    assert round_price(84.256) == 84.26
    assert round_price(90) == 90.0


def test_round_mw_two_decimals():
    assert round_mw(1.23456) == 1.23


def test_round_mwh_zero_decimals():
    assert round_mwh(8760.4) == 8760.0
    assert round_mwh(-1200.6) == -1201.0
