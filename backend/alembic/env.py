from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection

from app.core.config import Settings
from app.core.db import create_db_engine
from app.models import Base

config = context.config


def run_migrations(connection: Connection) -> None:
    # render_as_batch: SQLite can't ALTER most things, so Alembic rebuilds tables instead.
    context.configure(connection=connection, target_metadata=Base.metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    raise SystemExit("Offline (--sql) migrations are not supported; run against a database.")

if (connection := config.attributes.get("connection")) is not None:
    # Called from app code (startup, seed CLI, tests) with an open connection.
    run_migrations(connection)
else:
    # Called from the alembic CLI.
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)
    engine = create_db_engine(Settings().database_url)
    with engine.begin() as cli_connection:
        run_migrations(cli_connection)
    engine.dispose()
