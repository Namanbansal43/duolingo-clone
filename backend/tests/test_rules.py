"""Hearts and streak rules on their own, without a database."""

from datetime import UTC, date, datetime, timedelta

import pytest

from app.services.hearts import HeartsStatus, hearts_status
from app.services.streak import StreakStatus, local_date, streak_status

REGEN = timedelta(minutes=30)
T0 = datetime(2026, 10, 8, 12, 0, tzinfo=UTC)
TODAY = date(2026, 10, 8)


def hearts_after(stored: int, minutes: int) -> HeartsStatus:
    return hearts_status(
        stored=stored, max_hearts=5, updated_at=T0, now=T0 + timedelta(minutes=minutes), regen_every=REGEN
    )


def test_full_hearts_have_no_timer() -> None:
    assert hearts_after(5, 0) == HeartsStatus(current=5, max=5, next_heart_at=None)


def test_no_heart_before_a_full_interval() -> None:
    assert hearts_after(1, 29) == HeartsStatus(current=1, max=5, next_heart_at=T0 + REGEN)


def test_one_heart_per_interval() -> None:
    assert hearts_after(1, 60) == HeartsStatus(current=3, max=5, next_heart_at=T0 + 3 * REGEN)


def test_hearts_never_exceed_the_maximum() -> None:
    assert hearts_after(0, 10_000) == HeartsStatus(current=5, max=5, next_heart_at=None)


def test_clock_behind_the_anchor_regenerates_nothing() -> None:
    assert hearts_after(2, -15).current == 2


def test_no_streak_before_any_activity() -> None:
    assert streak_status(current=0, longest=0, last_date=None, today=TODAY) == StreakStatus(0, False, 0)


@pytest.mark.parametrize(
    ("days_ago", "expected"),
    [(0, StreakStatus(4, True, 9)), (1, StreakStatus(4, False, 9)), (2, StreakStatus(0, False, 9))],
)
def test_streak_survives_one_quiet_day_only(days_ago: int, expected: StreakStatus) -> None:
    last = TODAY - timedelta(days=days_ago)
    assert streak_status(current=4, longest=9, last_date=last, today=TODAY) == expected


def test_local_date_uses_the_learner_time_zone() -> None:
    evening_utc = datetime(2026, 10, 8, 20, 0, tzinfo=UTC)
    assert local_date(evening_utc, "UTC") == date(2026, 10, 8)
    assert local_date(evening_utc, "Asia/Kolkata") == date(2026, 10, 9)  # 01:30 the next day
