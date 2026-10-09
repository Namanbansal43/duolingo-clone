from datetime import timedelta

from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.core.clock import Clock
from app.core.config import Settings
from app.core.errors import error_response
from app.deps import ClockDep, CurrentUser, DbSession, SettingsDep
from app.models import User
from app.schemas.course import CourseOut
from app.schemas.me import HeartsOut, MeOut, MeUpdate, Onboarding, StreakOut
from app.services.hearts import hearts_status
from app.services.learner import lessons_completed, start_as_new_learner, update_learner, xp_earned_on
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


def _me_out(db: Session, user: User, clock: Clock, settings: Settings) -> MeOut:
    now = clock.now()
    today = local_date(now, user.timezone)
    hearts = hearts_status(
        stored=user.hearts,
        max_hearts=user.max_hearts,
        updated_at=user.hearts_updated_at,
        now=now,
        regen_every=timedelta(minutes=settings.heart_regen_minutes),
    )
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
        hearts=HeartsOut(
            current=hearts.current,
            max=hearts.max,
            next_heart_at=hearts.next_heart_at,
            regen_minutes=settings.heart_regen_minutes,
        ),
        streak=StreakOut(length=streak.length, extended_today=streak.extended_today, longest=streak.longest),
    )
