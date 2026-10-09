from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol


class Clock(Protocol):
    """Source of the current time. Injected so tests (and demo time travel) can control it."""

    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)


@dataclass(frozen=True)
class ShiftedClock:
    """Another clock, running `offset` ahead: the app's time after "Advance a day" on the settings page."""

    base: Clock
    offset: timedelta

    def now(self) -> datetime:
        return self.base.now() + self.offset
