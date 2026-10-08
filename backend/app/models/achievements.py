"""Achievements with levels, e.g. "Wildfire": reach a 3, 7, 14 then 30 day streak."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, ForeignKey, ForeignKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UTCDateTime, one_of


class AchievementMetric(StrEnum):
    """The learner statistic an achievement's thresholds are compared with."""

    STREAK = "streak"
    TOTAL_XP = "total_xp"
    LESSONS_COMPLETED = "lessons_completed"
    PERFECT_LESSONS = "perfect_lessons"


class Achievement(Base):
    __tablename__ = "achievements"
    __table_args__ = (CheckConstraint(one_of("metric", AchievementMetric), name="metric_known"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(32), unique=True)  # stable code name: "wildfire"
    position: Mapped[int]  # display order on the profile
    title: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(String(255))  # "Reach a {threshold} day streak"
    metric: Mapped[str] = mapped_column(String(32))

    tiers: Mapped[list["AchievementTier"]] = relationship(
        back_populates="achievement",
        order_by="AchievementTier.tier",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class AchievementTier(Base):
    """One level of an achievement and the value needed to reach it."""

    __tablename__ = "achievement_tiers"
    __table_args__ = (CheckConstraint("tier >= 1 AND threshold > 0", name="tier_and_threshold_positive"),)

    achievement_id: Mapped[int] = mapped_column(
        ForeignKey("achievements.id", ondelete="CASCADE"), primary_key=True
    )
    tier: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    threshold: Mapped[int]

    achievement: Mapped[Achievement] = relationship(back_populates="tiers")


class UserAchievement(Base):
    """A tier a learner has unlocked, and when."""

    __tablename__ = "user_achievements"
    __table_args__ = (
        ForeignKeyConstraint(
            ["achievement_id", "tier"],
            ["achievement_tiers.achievement_id", "achievement_tiers.tier"],
            ondelete="CASCADE",
        ),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    achievement_id: Mapped[int] = mapped_column(primary_key=True)
    tier: Mapped[int] = mapped_column(primary_key=True, autoincrement=False)
    unlocked_at: Mapped[datetime] = mapped_column(UTCDateTime)
