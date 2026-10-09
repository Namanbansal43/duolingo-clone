from dataclasses import dataclass
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class StreakStatus:
    length: int
    extended_today: bool
    longest: int


def local_date(moment: datetime, timezone: str) -> date:
    """The learner's calendar date at `moment`; streak days follow the learner's clock, not UTC."""
    return moment.astimezone(ZoneInfo(timezone)).date()


def streak_status(*, current: int, longest: int, last_date: date | None, today: date) -> StreakStatus:
    """The stored streak only changes when a lesson is finished. If neither today nor yesterday
    counted, the streak has lapsed and reads as 0, without a nightly job resetting it."""
    if last_date is None or last_date < today - timedelta(days=1):
        return StreakStatus(length=0, extended_today=False, longest=longest)
    return StreakStatus(length=current, extended_today=last_date >= today, longest=longest)


@dataclass(frozen=True)
class StreakUpdate:
    current: int
    longest: int
    last_date: date
    extended: bool  # whether this activity was the first to count today


def extend_streak(*, current: int, longest: int, last_date: date | None, today: date) -> StreakUpdate:
    """Record activity today: the first finished lesson of a day adds one to the streak if yesterday
    counted too, and starts a new streak of 1 if it didn't. Later lessons the same day change nothing."""
    if last_date == today:
        return StreakUpdate(current=current, longest=longest, last_date=today, extended=False)
    length = current + 1 if last_date == today - timedelta(days=1) else 1
    return StreakUpdate(current=length, longest=max(longest, length), last_date=today, extended=True)
