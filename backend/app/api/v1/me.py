from typing import Annotated

from fastapi import APIRouter, Query

from app.api.v1.views import achievement_out, me_out, regen_every
from app.core.errors import error_response
from app.deps import ClockDep, CurrentUser, DbSession, SettingsDep
from app.schemas.achievement import AchievementOut
from app.schemas.me import DailyXpOut, MeOut, MeUpdate, Onboarding
from app.schemas.settings import UserSettingsOut, UserSettingsUpdate
from app.services.achievements import achievement_progress
from app.services.learner import (
    daily_xp,
    learner_settings,
    refill_hearts,
    start_as_new_learner,
    update_learner,
    update_settings,
)
from app.services.streak import local_date

router = APIRouter(
    prefix="/me",
    tags=["me"],
    responses={503: error_response("`learner_missing`: the default learner has not been seeded.")},
)


@router.get("", response_model=MeOut)
def get_me(user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep) -> MeOut:
    """The logged-in learner with live stats: hearts after regeneration, streak and XP as of today."""
    return me_out(db, user, clock, settings)


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
    return me_out(db, user, clock, settings)


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
    return me_out(db, user, clock, settings)


@router.post(
    "/hearts/refill",
    response_model=MeOut,
    responses={409: error_response("`hearts_full`, or `not_enough_gems` (a refill costs 350 gems).")},
)
def refill_my_hearts(user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep) -> MeOut:
    """Refill hearts to full for 350 gems (a mocked purchase: gems are never bought with money)."""
    refill_hearts(db, user, clock.now(), regen_every(settings))
    return me_out(db, user, clock, settings)


@router.get("/settings", response_model=UserSettingsOut)
def get_my_settings(user: CurrentUser, db: DbSession) -> UserSettingsOut:
    """The learner's preferences from the settings page."""
    settings = learner_settings(db, user)
    db.commit()
    return UserSettingsOut.model_validate(settings)


@router.patch(
    "/settings",
    response_model=UserSettingsOut,
    responses={422: error_response("`validation_error`: a field is invalid or unknown; see `details`.")},
)
def update_my_settings(changes: UserSettingsUpdate, user: CurrentUser, db: DbSession) -> UserSettingsOut:
    """Change some preferences: sound effects, animations, motivational messages, listening exercises
    or dark mode. Omitted fields are left unchanged."""
    return UserSettingsOut.model_validate(update_settings(db, user, changes))


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
