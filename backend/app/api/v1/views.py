"""Response pieces that several routers return."""

from datetime import datetime, timedelta

from app.core.config import Settings
from app.models import User
from app.schemas.me import HeartsOut
from app.services.hearts import live_hearts


def regen_every(settings: Settings) -> timedelta:
    return timedelta(minutes=settings.heart_regen_minutes)


def hearts_out(user: User, now: datetime, settings: Settings) -> HeartsOut:
    """The learner's hearts right now, after regeneration."""
    hearts = live_hearts(user, now, regen_every(settings))
    return HeartsOut(
        current=hearts.current,
        max=hearts.max,
        next_heart_at=hearts.next_heart_at,
        regen_minutes=settings.heart_regen_minutes,
    )
