from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, Engine, create_engine, event, make_url

from app.core.config import BACKEND_DIR


def create_db_engine(url: str) -> Engine:
    """SQLite engine with foreign keys enforced (SQLite ignores them unless asked on every connection)."""
    database = make_url(url).database
    if database and database != ":memory:":
        Path(database).parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(url, connect_args={"check_same_thread": False})
    event.listen(engine, "connect", _enable_foreign_keys)
    return engine


def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def run_migrations(engine: Engine, revision: str = "head") -> None:
    """Apply Alembic migrations on the given engine (used at startup, by the seed CLI and in tests)."""
    with _migration_connection(engine) as (config, connection):
        config.attributes["connection"] = connection
        command.upgrade(config, revision)


def reset_database(engine: Engine) -> None:
    """Roll every migration back, then forward again: an empty schema with nothing seeded."""
    with _migration_connection(engine) as (config, connection):
        config.attributes["connection"] = connection
        command.downgrade(config, "base")
        command.upgrade(config, "head")


@contextmanager
def _migration_connection(engine: Engine) -> Iterator[tuple[Config, Connection]]:
    try:
        with engine.begin() as connection:
            yield Config(str(BACKEND_DIR / "alembic.ini")), connection
    finally:
        # Migrations switch foreign keys off on their connection (see alembic/env.py). Close every
        # pooled connection so the app only ever gets fresh ones, which turn them back on.
        engine.dispose()
