"""State of the demo tools on the settings page."""

from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DemoClock(Base):
    """How far the app's clock runs ahead of real time, after "Advance a day" on the settings page.

    A single row (id 1). Streaks, hearts and league weeks all follow the app's clock, so moving it
    forward lets a reviewer see a day or a week pass without waiting. No row means no time travel.
    """

    __tablename__ = "demo_clock"
    __table_args__ = (
        CheckConstraint("id = 1", name="single_row"),
        CheckConstraint("days_ahead >= 0", name="days_ahead_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    days_ahead: Mapped[int] = mapped_column(default=0)
