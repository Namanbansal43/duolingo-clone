from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.main import create_app
from app.models import User

NOW = datetime(2026, 10, 8, 12, 0, tzinfo=UTC)


class FixedClock:
    """A clock that only moves when a test moves it."""

    def __init__(self, now: datetime) -> None:
        self.current = now

    def now(self) -> datetime:
        return self.current

    def advance(self, delta: timedelta) -> None:
        self.current += delta


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(NOW)


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    # A fresh SQLite file per test; _env_file=None keeps a developer's backend/.env out of tests.
    return Settings(_env_file=None, database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}")


@pytest.fixture
def app(settings: Settings, clock: FixedClock) -> FastAPI:
    return create_app(settings, clock=clock)


@pytest.fixture
def client(app: FastAPI) -> Iterator[TestClient]:
    with TestClient(app) as test_client:  # entering runs startup: migrations, then seed
        yield test_client


@pytest.fixture
def db(app: FastAPI, client: TestClient) -> Iterator[Session]:
    with app.state.session_factory() as session:
        yield session


@pytest.fixture
def learner(db: Session, settings: Settings) -> User:
    return db.scalars(select(User).where(User.username == settings.default_username)).one()
