"""Tests fuer Mengen-/Vorzeichenvalidierung (Arbeitspaket 3)."""

import pytest

from src.domain.limit_order_logic import (
    TRIGGER_PARTNER_BUYS_LT,
    TRIGGER_PARTNER_SELLS_GT,
)
from src.domain.validation import (
    SIGN_NEGATIVE,
    SIGN_POSITIVE,
    all_nonzero_match_sign,
    at_least_one_nonzero,
    expected_sign_for_direction,
    expected_sign_for_trigger_condition,
    validate_trade_quantities,
)


def test_expected_sign_for_trigger_condition():
    assert expected_sign_for_trigger_condition(TRIGGER_PARTNER_BUYS_LT) == SIGN_POSITIVE
    assert (
        expected_sign_for_trigger_condition(TRIGGER_PARTNER_SELLS_GT) == SIGN_NEGATIVE
    )


def test_expected_sign_for_direction():
    assert expected_sign_for_direction("partner_buys") == SIGN_POSITIVE
    assert expected_sign_for_direction("partner_sells") == SIGN_NEGATIVE


def test_expected_sign_unknown_raises():
    with pytest.raises(ValueError):
        expected_sign_for_direction("unbekannt")


def test_expected_sign_for_trigger_condition_unknown_raises():
    with pytest.raises(ValueError):
        expected_sign_for_trigger_condition("unbekannt")


def test_at_least_one_nonzero():
    assert at_least_one_nonzero([0, 0, 5000, 0, 0]) is True
    assert at_least_one_nonzero([0, 0, 0, 0, 0]) is False


def test_all_nonzero_match_sign_ignores_zeros():
    # Nullen sind erlaubt; nur befuellte Mengen muessen zum Vorzeichen passen.
    assert all_nonzero_match_sign([0, 5000, 0, 3000, 0], SIGN_POSITIVE) is True
    assert all_nonzero_match_sign([0, 5000, -1, 0, 0], SIGN_POSITIVE) is False
    assert all_nonzero_match_sign([0, -5000, 0, -3000, 0], SIGN_NEGATIVE) is True
    assert all_nonzero_match_sign([0, -5000, 1, 0, 0], SIGN_NEGATIVE) is False


def test_validate_partner_buys_ok():
    assert validate_trade_quantities([0, 8760, 0, 0, 0], SIGN_POSITIVE) == []


def test_validate_all_zero_fails():
    errors = validate_trade_quantities([0, 0, 0, 0, 0], SIGN_POSITIVE)
    assert len(errors) == 1
    assert "ungleich 0" in errors[0]


def test_validate_wrong_sign_fails():
    errors = validate_trade_quantities([0, -8760, 0, 0, 0], SIGN_POSITIVE)
    assert any("positiv" in e for e in errors)


def test_validate_partner_sells_wrong_sign_fails():
    # Partner verkauft erfordert negative Mengen; eine positive Menge muss
    # die entsprechende Fehlermeldung ausloesen.
    errors = validate_trade_quantities([0, 8760, 0, 0, 0], SIGN_NEGATIVE)
    assert any("negativ" in e for e in errors)


def test_validate_reports_both_problems():
    # Alle Mengen 0 UND (leer) -> nur die "ungleich 0"-Meldung, da keine
    # befuellten Mengen das Vorzeichen verletzen koennen.
    errors = validate_trade_quantities([0, 0, 0, 0, 0], SIGN_NEGATIVE)
    assert errors == ["Mindestens ein Lieferjahr muss eine Menge ungleich 0 haben."]
