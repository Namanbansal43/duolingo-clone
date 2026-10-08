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
