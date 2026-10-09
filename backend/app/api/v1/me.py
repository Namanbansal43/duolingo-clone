from typing import Annotated

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.api.v1.views import achievement_out, hearts_out, regen_every
from app.core.clock import Clock
from app.core.config import Settings
from app.core.errors import error_response
from app.deps import ClockDep, CurrentUser, DbSession, SettingsDep
from app.models import User
from app.schemas.achievement import AchievementOut
from app.schemas.course import CourseOut
from app.schemas.me import DailyXpOut, MeOut, MeUpdate, Onboarding, StreakOut
from app.services.achievements import achievement_progress
from app.services.learner import (
    daily_xp,
    lessons_completed,
    refill_hearts,
    start_as_new_learner,
    update_learner,
    xp_earned_on,
)
from app.services.streak import local_date, streak_status

router = APIRouter(
    prefix="/me",
    tags=["me"],
    responses={503: error_response("`learner_missing`: the default learner has not been seeded.")},
)


@router.get("", response_model=MeOut)
def get_me(user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep) -> MeOut:
    """The logged-in learner with live stats: hearts after regeneration, streak and XP as of today."""
    return _me_out(db, user, clock, settings)


@router.patch(
    "",
    response_model=MeOut,
    responses={
        404: error_response("`course_not_found`: no course has that id."),
        409: error_response("`course_unavailable`: that course is coming soon."),
        422: error_response("`validation_error`: a field is invalid or not editable; see `details`."),
    },
)
def update_me(
    changes: MeUpdate, user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep
) -> MeOut:
    """Set the active course, daily goal or time zone, keeping the learner's progress."""
    update_learner(db, user, changes)
    return _me_out(db, user, clock, settings)


@router.post(
    "/onboarding",
    response_model=MeOut,
    responses={
        404: error_response("`course_not_found`: no course has that id."),
        409: error_response("`course_unavailable`: that course is coming soon."),
        422: error_response("`validation_error`: a field is missing, invalid or unknown; see `details`."),
    },
)
def complete_onboarding(
    choices: Onboarding, user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep
) -> MeOut:
    """Finish the "Get started" flow. The learner starts over as a new account: their history
    (lessons, XP, path progress, achievements) is cleared, their stats are reset (0 XP, no streak,
    full hearts, 500 gems), and the chosen course, daily goal and time zone are saved. The path
    starts again at its first node."""
    start_as_new_learner(db, user, choices, clock.now())
    return _me_out(db, user, clock, settings)


@router.post(
    "/hearts/refill",
    response_model=MeOut,
    responses={409: error_response("`hearts_full`, or `not_enough_gems` (a refill costs 350 gems).")},
)
def refill_my_hearts(user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep) -> MeOut:
    """Refill hearts to full for 350 gems (a mocked purchase: gems are never bought with money)."""
    refill_hearts(db, user, clock.now(), regen_every(settings))
    return _me_out(db, user, clock, settings)


@router.get("/achievements", response_model=list[AchievementOut])
def get_my_achievements(user: CurrentUser, db: DbSession) -> list[AchievementOut]:
    """Every achievement, with the learner's level and progress towards the next one."""
    return [achievement_out(progress) for progress in achievement_progress(db, user)]


@router.get(
    "/xp-history",
    response_model=list[DailyXpOut],
    responses={422: error_response("`validation_error`: `days` must be between 1 and 31.")},
)
def get_my_xp_history(
    user: CurrentUser,
    db: DbSession,
    clock: ClockDep,
    days: Annotated[int, Query(ge=1, le=31, description="How many days, ending today.")] = 7,
) -> list[DailyXpOut]:
    """XP earned on each of the last `days` days, ending today in the learner's time zone, oldest first.
    Days without XP are included with 0. The profile's "XP this week" chart shows the last 7."""
    today = local_date(clock.now(), user.timezone)
    return [DailyXpOut(day=day, xp=xp) for day, xp in daily_xp(db, user, today, days)]


def _me_out(db: Session, user: User, clock: Clock, settings: Settings) -> MeOut:
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
        active_course=CourseOut.model_validate(user.active_course) if user.active_course else None,
        daily_goal_xp=user.daily_goal_xp,
        total_xp=user.total_xp,
        xp_today=xp_earned_on(db, user, today),
        lessons_completed=lessons_completed(db, user),
        gems=user.gems,
        hearts=hearts_out(user, now, settings),
        streak=StreakOut(length=streak.length, extended_today=streak.extended_today, longest=streak.longest),
    )
