"""The demo tools on the settings page: move the app's clock forward, empty the hearts, start over.

The brief allows streak and day logic to be simulated; these make it testable from the browser.
"""

from datetime import datetime, timedelta

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.core.clock import Clock, ShiftedClock
from app.models import DemoClock, User
from app.seed import seed_database
from app.services.learner import preferences, set_preferences


def days_ahead(db: Session) -> int:
    """How many days the app's clock runs ahead of real time (0 until a day is advanced)."""
    row = db.get(DemoClock, 1)
    return row.days_ahead if row else 0


def app_clock(db: Session, real: Clock) -> Clock:
    """The clock every request uses: real time, plus any days advanced with the demo tools."""
    return ShiftedClock(real, timedelta(days=days_ahead(db)))


def advance_day(db: Session) -> int:
    """Move the app's clock forward by one day. Returns the new number of days ahead."""
    row = db.get(DemoClock, 1)
    if row is None:
        row = DemoClock(id=1, days_ahead=0)
        db.add(row)
    row.days_ahead += 1
    db.commit()
    return row.days_ahead


def empty_hearts(db: Session, user: User, now: datetime) -> None:
    """Take every heart away, to try the out-of-hearts flow. They regenerate from now as usual."""
    user.hearts = 0
    user.hearts_updated_at = now
    db.commit()


def reset_demo(db: Session, current: User, username: str, real_now: datetime) -> User:
    """Back to the state the app first starts in: the clock returns to real time, every learner (the
    guest and the rivals too) is removed with all their progress, and the seed runs again. Returns the
    re-seeded demo learner, who keeps the current learner's preferences from the settings page."""
    kept = preferences(db, current)

    db.execute(delete(DemoClock))
    db.execute(delete(User))  # the database cascades to progress, history, settings and rivals
    db.expunge_all()  # forget the deleted rows: the new learners may reuse their ids
    seed_database(db, default_username=username, now=real_now)

    learner = db.scalars(select(User).where(User.username == username)).one()
    set_preferences(db, learner, kept)
    db.commit()
    return learner
