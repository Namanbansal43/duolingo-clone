from typing import Annotated

from fastapi import APIRouter, Query, Request, Response

from app.api.v1.views import achievement_out, act_as_demo_learner, act_as_guest, me_out, regen_every
from app.core.errors import error_response
from app.deps import ClockDep, CurrentUser, DbSession, SettingsDep, demo_learner
from app.schemas.achievement import AchievementOut
from app.schemas.me import DailyXpOut, MeOut, MeUpdate, Onboarding
from app.schemas.settings import UserSettingsOut, UserSettingsUpdate
from app.services.achievements import achievement_progress
from app.services.learner import (
    daily_xp,
    learner_settings,
    preferences,
    refill_hearts,
    set_preferences,
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
    choices: Onboarding,
    user: CurrentUser,
    db: DbSession,
    clock: ClockDep,
    settings: SettingsDep,
    request: Request,
    response: Response,
) -> MeOut:
    """Finish the "Get started" flow: this browser becomes a guest learner, separate from the demo
    learner, whose progress is left alone. The guest starts with no history, 0 XP, no streak, full
    hearts and 500 gems, at the first node of the chosen course, with the chosen daily goal and time
    zone; preferences from the settings page carry over. Doing it again starts the guest over. The
    response sets the `learner` cookie that makes later requests act as the guest."""
    guest = start_as_new_learner(db, settings.guest_username, user, choices, clock.now())
    act_as_guest(request, response)
    return me_out(db, guest, clock, settings)


@router.post("/sign-in", response_model=MeOut)
def sign_in(
    user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep, response: Response
) -> MeOut:
    """Sign in to the demo account ("I already have an account"): this browser stops being the guest and
    acts as the demo learner again, with their progress. The brief assumes a logged-in learner, so there
    is no password. The guest's preferences carry over; its progress stays with the guest. Clears the
    `learner` cookie."""
    learner = demo_learner(db, settings)
    if user is not learner:
        set_preferences(db, learner, preferences(db, user))
        db.commit()
    act_as_demo_learner(response)
    return me_out(db, learner, clock, settings)


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
