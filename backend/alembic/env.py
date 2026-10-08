from logging.config import fileConfig

from alembic import context
from alembic.autogenerate.api import AutogenContext
from sqlalchemy import Connection

from app.core.config import Settings
from app.core.db import create_db_engine
from app.models import Base
from app.models.base import UTCDateTime

config = context.config


def render_item(type_: str, obj: object, _autogen_context: AutogenContext) -> str | bool:
    """Autogenerate writes UTCDateTime columns as plain DateTime, so migrations don't import app code."""
    if type_ == "type" and isinstance(obj, UTCDateTime):
        return "sa.DateTime()"
    return False


def run_migrations(connection: Connection) -> None:
    # SQLite can't ALTER most things, so batch mode rebuilds a table: copy it, drop the original,
    # rename the copy. With foreign keys on, SQLite treats that DROP as deleting every row and
    # cascades the deletes into child tables. So they are off while migrating (this PRAGMA only
    # works before the transaction starts) and every reference is verified at the end instead.
    connection.exec_driver_sql("PRAGMA foreign_keys = OFF")
    context.configure(
        connection=connection,
        target_metadata=Base.metadata,
        render_as_batch=True,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()
    broken = connection.exec_driver_sql("PRAGMA foreign_key_check").fetchall()
    if broken:
        raise RuntimeError(f"Migration left rows pointing at missing parents: {broken}")


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
