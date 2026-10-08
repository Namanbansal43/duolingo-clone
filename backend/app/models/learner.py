from datetime import date, datetime

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UTCDateTime
from app.models.content import Course

# Casual, Regular, Serious, Intense
DAILY_GOAL_OPTIONS = (10, 20, 30, 50)


class User(Base):
    """A learner and their game state.

    Hearts and streak are stored as of their last change; the live values (regenerated hearts,
    a lapsed streak) are derived on read by app.services, so no background job is needed.
    """

    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint(f"daily_goal_xp IN {DAILY_GOAL_OPTIONS}", name="daily_goal_option"),
        CheckConstraint("total_xp >= 0", name="total_xp_non_negative"),
        CheckConstraint("gems >= 0", name="gems_non_negative"),
        CheckConstraint("max_hearts > 0 AND hearts BETWEEN 0 AND max_hearts", name="hearts_in_range"),
        CheckConstraint("current_streak >= 0 AND longest_streak >= current_streak", name="streak_valid"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    display_name: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")  # IANA name; decides "today"

    active_course_id: Mapped[int | None] = mapped_column(ForeignKey("courses.id", ondelete="SET NULL"))
    daily_goal_xp: Mapped[int] = mapped_column(default=20)

    total_xp: Mapped[int] = mapped_column(default=0)
    gems: Mapped[int] = mapped_column(default=0)

    hearts: Mapped[int] = mapped_column(default=5)
    max_hearts: Mapped[int] = mapped_column(default=5)
    hearts_updated_at: Mapped[datetime] = mapped_column(UTCDateTime)  # regeneration counts from here

    current_streak: Mapped[int] = mapped_column(default=0)
    longest_streak: Mapped[int] = mapped_column(default=0)
    last_streak_date: Mapped[date | None]  # learner's local date of the last day that counted

    active_course: Mapped[Course | None] = relationship()
