"""Tests fuer Positions- und Limitlogik (Arbeitspaket 3/4)."""

import pytest

from src.domain.position_logic import (
    STATUS_LIMIT_BREACHED,
    STATUS_WITHIN_LIMIT,
    is_limit_breached,
    limit_status,
    simulated_position_mw,
    utilization_pct,
)


def test_simulated_position_is_sum():
    assert simulated_position_mw(0.8, -0.3) == pytest.approx(0.5)


@pytest.mark.parametrize(
    "position_mw, breached",
    [
        (0.5, False),
        (1.0, False),   # genau am Limit ist nicht verletzt
        (-1.0, False),
        (1.01, True),
        (-1.5, True),   # Limit gilt auf den Absolutwert
    ],
)
def test_is_limit_breached_on_absolute_value(position_mw, breached):
    assert is_limit_breached(position_mw) is breached


def test_utilization_pct():
    assert utilization_pct(0.5) == pytest.approx(50.0)
    assert utilization_pct(-1.5) == pytest.approx(150.0)


def test_limit_status_text():
    assert limit_status(0.5) == STATUS_WITHIN_LIMIT
    assert limit_status(-1.2) == STATUS_LIMIT_BREACHED
