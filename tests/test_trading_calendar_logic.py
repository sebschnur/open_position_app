"""Tests fuer Handelskalender-Faelligkeit (Arbeitspaket 3/7).

Das heutige Datum wird injiziert, damit die Tests unabhaengig vom echten
Kalendertag sind.
"""

import datetime as dt

from src.domain.trading_calendar_logic import (
    STATUS_DELETED,
    STATUS_DONE,
    STATUS_PLANNED,
    is_due,
    is_visible_in_standard_view,
)

TODAY = dt.date(2026, 7, 4)


def test_due_when_date_today_and_not_done():
    assert is_due(TODAY, STATUS_PLANNED, today=TODAY) is True


def test_due_when_date_in_past_and_not_done():
    assert is_due(TODAY - dt.timedelta(days=3), STATUS_PLANNED, today=TODAY) is True


def test_not_due_when_date_in_future():
    assert is_due(TODAY + dt.timedelta(days=1), STATUS_PLANNED, today=TODAY) is False


def test_not_due_when_done_even_if_overdue():
    assert is_due(TODAY - dt.timedelta(days=5), STATUS_DONE, today=TODAY) is False


def test_visibility_hides_done_and_deleted():
    assert is_visible_in_standard_view(STATUS_PLANNED) is True
    assert is_visible_in_standard_view(STATUS_DONE) is False
    assert is_visible_in_standard_view(STATUS_DELETED) is False
