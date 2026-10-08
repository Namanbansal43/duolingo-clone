from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    """Source of the current time. Injected so tests (and later, demo time travel) can control it."""

    def now(self) -> datetime: ...


class SystemClock:
    def now(self) -> datetime:
        return datetime.now(UTC)
