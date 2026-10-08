from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class HeartsStatus:
    current: int
    max: int
    next_heart_at: datetime | None  # None when full


def hearts_status(
    *, stored: int, max_hearts: int, updated_at: datetime, now: datetime, regen_every: timedelta
) -> HeartsStatus:
    """Hearts come back one at a time, one per `regen_every` since `updated_at`.

    Nothing is written here: the live count is derived from the stored count and the elapsed time
    whenever it is read, so no scheduled job has to top hearts up.
    """
    if stored >= max_hearts:
        return HeartsStatus(current=max_hearts, max=max_hearts, next_heart_at=None)

    regenerated = max(now - updated_at, timedelta(0)) // regen_every
    current = min(max_hearts, stored + regenerated)
    next_heart_at = None if current == max_hearts else updated_at + (regenerated + 1) * regen_every
    return HeartsStatus(current=current, max=max_hearts, next_heart_at=next_heart_at)
