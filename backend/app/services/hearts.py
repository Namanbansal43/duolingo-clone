from dataclasses import dataclass
from datetime import datetime, timedelta

from app.models import User


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


def change_hearts(
    *, stored: int, max_hearts: int, updated_at: datetime, now: datetime, regen_every: timedelta, delta: int
) -> tuple[int, datetime]:
    """Add (or with a negative delta, spend) hearts on top of the live count. Returns the new stored count
    and the moment regeneration counts from.

    Hearts that already came back are kept, and so is the time towards the next one; only when the count
    was full, or ends up full, does the regeneration clock restart from now.
    """
    current = hearts_status(
        stored=stored, max_hearts=max_hearts, updated_at=updated_at, now=now, regen_every=regen_every
    ).current
    target = max(0, min(max_hearts, current + delta))
    if current >= max_hearts or target >= max_hearts:
        return target, now
    return target, updated_at + (current - stored) * regen_every


def live_hearts(user: User, now: datetime, regen_every: timedelta) -> HeartsStatus:
    return hearts_status(
        stored=user.hearts,
        max_hearts=user.max_hearts,
        updated_at=user.hearts_updated_at,
        now=now,
        regen_every=regen_every,
    )


def add_hearts(user: User, delta: int, now: datetime, regen_every: timedelta) -> None:
    """Give the learner hearts, or take them with a negative delta (see change_hearts)."""
    user.hearts, user.hearts_updated_at = change_hearts(
        stored=user.hearts,
        max_hearts=user.max_hearts,
        updated_at=user.hearts_updated_at,
        now=now,
        regen_every=regen_every,
        delta=delta,
    )
