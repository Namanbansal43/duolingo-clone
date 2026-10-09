from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.config import Config
from alembic.runtime.migration import MigrationContext
from sqlalchemy import func, inspect, select, text
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, Settings
from app.core.db import create_db_engine, reset_database, run_migrations
from app.models import (
    Achievement,
    AchievementTier,
    Base,
    Course,
    League,
    LeagueMembership,
    Rival,
    User,
    UserSettings,
)
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
    tables = set(inspect(engine).get_table_names()) - {"alembic_version"}
    engine.dispose()

    assert tables == set(Base.metadata.tables)
    assert len(tables) == 20


def test_upgrading_keeps_existing_learners(settings: Settings) -> None:
    """Later migrations rebuild the users table (0002 adds streak_freezes, 0005 is_guest); the rows must
    survive each copy."""
    engine = create_db_engine(settings.database_url)
    run_migrations(engine, "0001")
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO courses (id, learning_language, from_language, title, position, is_available) "
                "VALUES (1, 'es', 'en', 'Spanish', 0, 1)"
            )
        )
        connection.execute(
            text(
                "INSERT INTO users (id, username, display_name, created_at, timezone, active_course_id, "
                "daily_goal_xp, total_xp, gems, hearts, max_hearts, hearts_updated_at, current_streak, "
                "longest_streak) VALUES (7, 'early_bird', 'Early Bird', '2026-10-01 09:00:00', 'UTC', 1, "
                "30, 120, 45, 4, 5, '2026-10-01 09:00:00', 2, 5)"
            )
        )

    run_migrations(engine)

    with engine.connect() as connection:
        row = connection.execute(
            text("SELECT username, active_course_id, total_xp, gems, streak_freezes, is_guest FROM users")
        ).one()
        foreign_keys_on = connection.execute(text("PRAGMA foreign_keys")).scalar()
    engine.dispose()

    assert tuple(row) == ("early_bird", 1, 120, 45, 0, 0)  # existing learners have profiles
    assert foreign_keys_on == 1  # migrations turn them off; app connections must get them back


def test_upgrading_turns_dark_mode_into_a_choice(settings: Settings) -> None:
    """Before 0007 dark mode was a flag nobody could change, so "off" was only the default."""
    engine = create_db_engine(settings.database_url)
    run_migrations(engine, "0006")
    with engine.begin() as connection:
        for user_id, dark in [(1, 0), (2, 1)]:
            connection.execute(
                text(
                    "INSERT INTO users (id, username, display_name, created_at, timezone, daily_goal_xp, "
                    "total_xp, gems, hearts, max_hearts, hearts_updated_at, current_streak, longest_streak) "
                    f"VALUES ({user_id}, 'u{user_id}', 'U', '2026-10-01', 'UTC', 20, 0, 0, 5, 5, "
                    "'2026-10-01', 0, 0)"
                )
            )
            connection.execute(text(f"INSERT INTO user_settings VALUES ({user_id}, 1, 1, 1, 1, {dark})"))

    run_migrations(engine)

    with engine.connect() as connection:
        rows = connection.execute(text("SELECT user_id, dark_mode FROM user_settings ORDER BY user_id")).all()
    engine.dispose()

    assert [tuple(row) for row in rows] == [(1, "system"), (2, "on")]


def test_seeding_again_adds_nothing_and_keeps_progress(
    db: Session, learner: User, settings: Settings, clock: FixedClock
) -> None:
    learner.gems = 42
    learner.settings.sound_effects = False
    db.commit()

    seed_database(db, default_username=settings.default_username, now=clock.now())

    def count(model: type[Base]) -> int:
        return db.scalar(select(func.count()).select_from(model))

    assert count(Course) == len(data.COURSES)
    assert count(Achievement) == len(data.ACHIEVEMENTS)
    assert count(AchievementTier) == sum(len(thresholds) for *_, thresholds in data.ACHIEVEMENTS)
    assert count(League) == len(data.LEAGUES)
    assert count(User) == 1 + count(Rival) == 1 + len(data.RIVALS)
    assert count(UserSettings) == 1  # rivals have no settings page
    assert count(LeagueMembership) == 1 + len(data.RIVALS)  # this week's league
    db.refresh(learner)
    assert learner.gems == 42
    assert learner.settings.sound_effects is False


def test_downgrading_keeps_listening_exercises_as_word_banks(settings: Settings) -> None:
    engine = create_db_engine(settings.database_url)
    run_migrations(engine)
    with engine.begin() as connection:
        for statement in [
            "INSERT INTO courses (id, learning_language, from_language, title, position, is_available) "
            "VALUES (1, 'es', 'en', 'Spanish', 0, 1)",
            "INSERT INTO units (id, course_id, position, title) VALUES (1, 1, 1, 'Unit')",
            "INSERT INTO skills (id, unit_id, position, title, kind) VALUES (1, 1, 1, 'Say hello', 'lesson')",
            "INSERT INTO lessons (id, skill_id, position) VALUES (1, 1, 1)",
            "INSERT INTO exercises (id, lesson_id, position, type, prompt, prompt_language) "
            "VALUES (1, 1, 1, 'listen', 'Hola.', 'es')",
        ]:
            connection.execute(text(statement))

    config = Config(str(BACKEND_DIR / "alembic.ini"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "0003")

    with engine.connect() as connection:
        kind = connection.execute(text("SELECT type FROM exercises WHERE id = 1")).scalar()
    engine.dispose()
    assert kind == "word_bank"
