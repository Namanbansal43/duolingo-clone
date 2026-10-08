from datetime import datetime

import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import func, inspect, select
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.db import create_db_engine, reset_database, run_migrations
from app.models import Base, Course, User
from app.seed import data, seed_database
from tests.conftest import FixedClock


def test_migrations_match_the_models(settings: Settings) -> None:
    engine = create_db_engine(settings.database_url)
    run_migrations(engine)
    with engine.connect() as connection:
        drift = compare_metadata(MigrationContext.configure(connection), Base.metadata)
    engine.dispose()

    assert drift == []


def test_migrations_roll_back_and_forward(settings: Settings) -> None:
    engine = create_db_engine(settings.database_url)
    run_migrations(engine)
    reset_database(engine)
    tables = set(inspect(engine).get_table_names())
    engine.dispose()

    assert {"courses", "users"} <= tables


def test_seeding_again_adds_nothing_and_keeps_progress(
    db: Session, learner: User, settings: Settings, clock: FixedClock
) -> None:
    learner.gems = 42
    db.commit()

    seed_database(db, default_username=settings.default_username, now=clock.now())

    assert db.scalar(select(func.count()).select_from(Course)) == len(data.COURSES)
    assert db.scalar(select(func.count()).select_from(User)) == 1
    db.refresh(learner)
    assert learner.gems == 42


def test_foreign_keys_are_enforced(db: Session, learner: User) -> None:
    learner.active_course_id = 9999
    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        db.commit()


@pytest.mark.parametrize(
    ("column", "value"),
    [("hearts", 6), ("gems", -1), ("daily_goal_xp", 15), ("longest_streak", -1)],
)
def test_check_constraints_guard_learner_state(db: Session, learner: User, column: str, value: int) -> None:
    setattr(learner, column, value)
    with pytest.raises(IntegrityError, match="CHECK"):
        db.commit()


def test_naive_datetimes_are_refused(db: Session, learner: User) -> None:
    learner.hearts_updated_at = datetime(2026, 10, 8, 12, 0)  # no time zone
    with pytest.raises(StatementError, match="naive datetime"):
        db.commit()
