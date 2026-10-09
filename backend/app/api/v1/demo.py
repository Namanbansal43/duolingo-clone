from fastapi import APIRouter, Response
from sqlalchemy.orm import Session

from app.api.v1.views import act_as_demo_learner, me_out
from app.core.clock import Clock
from app.deps import ClockDep, CurrentUser, DbSession, RealClockDep, SettingsDep
from app.schemas.demo import DemoClockOut
from app.schemas.me import MeOut
from app.services.demo import advance_day, app_clock, days_ahead, empty_hearts, reset_demo

router = APIRouter(prefix="/demo", tags=["demo"])


@router.get("/clock", response_model=DemoClockOut)
def get_demo_clock(db: DbSession, real: RealClockDep) -> DemoClockOut:
    """How far the app's clock has been moved forward, and the time it shows now."""
    return _clock_out(db, real)


@router.post("/clock/advance", response_model=DemoClockOut)
def advance_demo_clock(db: DbSession, real: RealClockDep) -> DemoClockOut:
    """Move the app's clock forward one day. Everything goes by it: the next day a lesson extends the
    streak and a day without one breaks it, hearts regenerate, and rivals keep earning XP until the
    league week ends. Resetting the demo returns to real time."""
    advance_day(db)
    return _clock_out(db, real)


@router.post("/hearts/empty", response_model=MeOut)
def empty_my_hearts(user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep) -> MeOut:
    """Lose every heart, to try the out-of-hearts screen. They then regenerate as usual."""
    empty_hearts(db, user, clock.now())
    return me_out(db, user, clock, settings)


@router.post("/reset", response_model=MeOut)
def reset_the_demo(
    user: CurrentUser, db: DbSession, real: RealClockDep, settings: SettingsDep, response: Response
) -> MeOut:
    """Start the demo again: the clock returns to real time, the guest from "Get started" is removed, and
    the demo learner and the rivals go back to the seeded state (the demo learner has a 3 day streak and
    is in this week's Bronze league). This browser is the demo learner afterwards (the `learner` cookie
    is cleared). Preferences from the settings page are kept."""
    learner = reset_demo(db, user, settings.default_username, real.now())
    act_as_demo_learner(response)
    return me_out(db, learner, real, settings)


def _clock_out(db: Session, real: Clock) -> DemoClockOut:
    return DemoClockOut(days_ahead=days_ahead(db), now=app_clock(db, real).now())
