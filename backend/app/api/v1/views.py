"""Response pieces that several routers return."""

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.clock import Clock
from app.core.config import Settings
from app.models import User
from app.schemas.achievement import AchievementOut
from app.schemas.course import CourseOut
from app.schemas.me import HeartsOut, MeOut, StreakOut
from app.services.achievements import AchievementProgress
from app.services.hearts import live_hearts
from app.services.learner import lessons_completed, xp_earned_on
from app.services.streak import local_date, streak_status


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


def achievement_out(progress: AchievementProgress) -> AchievementOut:
    return AchievementOut(
        key=progress.achievement.key,
        title=progress.achievement.title,
        level=progress.level,
        max_level=progress.max_level,
        value=progress.value,
        goal=progress.goal,
        description=progress.description,
        unlocked_at=progress.unlocked_at,
    )


def me_out(db: Session, user: User, clock: Clock, settings: Settings) -> MeOut:
    """The learner with live stats, as of the app's clock."""
    now = clock.now()
    today = local_date(now, user.timezone)
    streak = streak_status(
        current=user.current_streak,
        longest=user.longest_streak,
        last_date=user.last_streak_date,
        today=today,
    )
    return MeOut(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        joined_at=user.created_at,
        timezone=user.timezone,
        is_guest=user.is_guest,
        active_course=CourseOut.model_validate(user.active_course) if user.active_course else None,
        daily_goal_xp=user.daily_goal_xp,
        total_xp=user.total_xp,
        xp_today=xp_earned_on(db, user, today),
        lessons_completed=lessons_completed(db, user),
        gems=user.gems,
        hearts=hearts_out(user, now, settings),
        streak=StreakOut(length=streak.length, extended_today=streak.extended_today, longest=streak.longest),
        now=now,
    )
