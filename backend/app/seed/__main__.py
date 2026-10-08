"""Create or update the database from the command line.

python -m app.seed           apply migrations, then add any missing seed data
python -m app.seed --reset   wipe everything (all progress too) and seed from scratch
"""

import argparse

from sqlalchemy.orm import Session

from app.core.clock import SystemClock
from app.core.config import Settings
from app.core.db import create_db_engine, reset_database, run_migrations
from app.seed import seed_database


def main() -> None:
    parser = argparse.ArgumentParser(prog="python -m app.seed", description="Create or update the database.")
    parser.add_argument("--reset", action="store_true", help="drop all data, including progress, first")
    args = parser.parse_args()

    settings = Settings()
    engine = create_db_engine(settings.database_url)
    if args.reset:
        reset_database(engine)
    else:
        run_migrations(engine)
    with Session(engine) as db:
        seed_database(db, default_username=settings.default_username, now=SystemClock().now())
    engine.dispose()
    print(f"Database ready: {settings.database_url}")


if __name__ == "__main__":
    main()
