"""The learner, their preferences and their progress through the path."""

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, ForeignKey, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UTCDateTime, one_of
from app.models.content import Course

# Casual, Regular, Serious, Intense
DAILY_GOAL_OPTIONS = (10, 20, 30, 50)
MAX_STREAK_FREEZES = 2


class DarkMode(StrEnum):
    """The settings page's dark mode choice, as on duolingo.com."""

    SYSTEM = "system"  # follow the device's light or dark setting
    ON = "on"
    OFF = "off"


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
        CheckConstraint(f"streak_freezes BETWEEN 0 AND {MAX_STREAK_FREEZES}", name="streak_freezes_in_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True)
    display_name: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime)
    timezone: Mapped[str] = mapped_column(String(64), default="UTC")  # IANA name; decides "today"
    # Started over through "Get started" without creating a profile. Sign-up is a placeholder, so like a
    # guest on duolingo.com they are asked to create a profile instead of seeing one.
    is_guest: Mapped[bool] = mapped_column(default=False, server_default=text("0"))

    active_course_id: Mapped[int | None] = mapped_column(ForeignKey("courses.id", ondelete="SET NULL"))
    daily_goal_xp: Mapped[int] = mapped_column(default=20)

    total_xp: Mapped[int] = mapped_column(default=0)  # running total of xp_events, kept for quick reads
    gems: Mapped[int] = mapped_column(default=0)

    hearts: Mapped[int] = mapped_column(default=5)
    max_hearts: Mapped[int] = mapped_column(default=5)
    hearts_updated_at: Mapped[datetime] = mapped_column(UTCDateTime)  # regeneration counts from here

    current_streak: Mapped[int] = mapped_column(default=0)
    longest_streak: Mapped[int] = mapped_column(default=0)
    last_streak_date: Mapped[date | None]  # learner's local date of the last day that counted
    # Bought in the shop; one is used up automatically to cover a missed day.
    streak_freezes: Mapped[int] = mapped_column(default=0, server_default=text("0"))

    active_course: Mapped[Course | None] = relationship()
    settings: Mapped["UserSettings | None"] = relationship(
        back_populates="user", cascade="all, delete-orphan", passive_deletes=True
    )


class UserSettings(Base):
    """Preferences from the settings page, one row per learner (kept off the busy users row)."""

    __tablename__ = "user_settings"
    __table_args__ = (CheckConstraint(one_of("dark_mode", DarkMode), name="dark_mode_known"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    sound_effects: Mapped[bool] = mapped_column(default=True)
    animations: Mapped[bool] = mapped_column(default=True)
    motivational_messages: Mapped[bool] = mapped_column(default=True)
    listening_exercises: Mapped[bool] = mapped_column(default=True)
    dark_mode: Mapped[str] = mapped_column(String(8), default=DarkMode.SYSTEM)

    user: Mapped[User] = relationship(back_populates="settings")


class UserSkillProgress(Base):
    """How far a learner is through one path node. No row yet means not started.

    Whether a node is locked is not stored: it follows from the previous node being completed.
    """

    __tablename__ = "user_skill_progress"
    __table_args__ = (CheckConstraint("lessons_completed >= 0", name="lessons_completed_non_negative"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    skill_id: Mapped[int] = mapped_column(ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    lessons_completed: Mapped[int] = mapped_column(default=0)  # drives the progress ring
    completed_at: Mapped[datetime | None] = mapped_column(UTCDateTime)  # all lessons done, or chest opened
