"""Tests fuer Schaltjahr- und Stundenlogik (Arbeitspaket 3)."""

import pytest

from src.domain.calendar_utils import hours_in_year, is_leap_year


@pytest.mark.parametrize(
    "year, expected",
    [
        (2024, True),  # durch 4 teilbar
        (2025, False),
        (2026, False),
        (2028, True),
        (1900, False),  # durch 100, nicht durch 400
        (2000, True),  # durch 400
        (2100, False),  # durch 100, nicht durch 400
    ],
)
def test_is_leap_year(year, expected):
    assert is_leap_year(year) is expected


@pytest.mark.parametrize(
    "year, expected_hours",
    [
        (2025, 8760),
        (2026, 8760),
        (2024, 8784),
        (2028, 8784),
        (2000, 8784),
        (1900, 8760),
    ],
)
def test_hours_in_year(year, expected_hours):
    assert hours_in_year(year) == expected_hours
