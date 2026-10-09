from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import Clock
from app.core.config import Settings
from app.core.errors import AppError
from app.models import User
from app.services.demo import app_clock


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_db(request: Request) -> Iterator[Session]:
    with request.app.state.session_factory() as session:
        yield session


SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSession = Annotated[Session, Depends(get_db)]


def get_real_clock(request: Request) -> Clock:
    return request.app.state.clock


RealClockDep = Annotated[Clock, Depends(get_real_clock)]


def get_clock(db: DbSession, real: RealClockDep) -> Clock:
    """The app's time: real time, moved forward by any days advanced with the demo tools."""
    return app_clock(db, real)


ClockDep = Annotated[Clock, Depends(get_clock)]


def get_current_user(db: DbSession, settings: SettingsDep) -> User:
    """The brief assumes a logged-in learner, so every request acts as the seeded default user.

    This is the only place that decides who "me" is: real authentication would replace this
    function (e.g. look the user up from a session cookie) and nothing else would change.
    """
    user = db.scalar(select(User).where(User.username == settings.default_username))
    if user is None:
        raise AppError(503, "learner_missing", "The default learner has not been seeded yet.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
