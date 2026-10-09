"""Weekly leagues: the ten leagues from Bronze to Diamond, who competed in which one each week, and the
seeded rivals the learner competes with."""

from datetime import date, datetime

from sqlalchemy import CheckConstraint, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UTCDateTime


class League(Base):
    """One of the ten leagues, and how many of its members move up or down at the end of a week."""

    __tablename__ = "leagues"
    __table_args__ = (
        CheckConstraint("position >= 1", name="position_positive"),
        CheckConstraint("promotion_count >= 0 AND demotion_count >= 0", name="zones_non_negative"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    position: Mapped[int] = mapped_column(unique=True)  # 1 Bronze ... 10 Diamond
    name: Mapped[str] = mapped_column(String(32), unique=True)  # "Bronze"
    promotion_count: Mapped[int]  # the top N move up a league (0 in Diamond)
    demotion_count: Mapped[int]  # the bottom N move down a league (0 in Bronze)


class LeagueMembership(Base):
    """A learner's place in one week's league. The members of a league in the same week compete with each
    other; the final rank is stored once that week is over."""

    __tablename__ = "league_memberships"
    __table_args__ = (
        CheckConstraint("final_rank IS NULL OR final_rank >= 1", name="final_rank_positive"),
        Index(None, "week_start", "league_id"),  # everyone competing in one league in one week
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    week_start: Mapped[date] = mapped_column(primary_key=True)  # the Monday the league week starts on
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id", ondelete="RESTRICT"))
    joined_at: Mapped[datetime] = mapped_column(UTCDateTime)
    final_rank: Mapped[int | None]

    league: Mapped[League] = relationship()


class Rival(Base):
    """A seeded learner the real learner competes with. Rivals don't play lessons: their XP follows a
    schedule worked out from their id and the date, and is written as ordinary xp_events whenever the
    leaderboard is read, up to that moment."""

    __tablename__ = "rivals"
    __table_args__ = (
        CheckConstraint("daily_xp > 0", name="daily_xp_positive"),
        CheckConstraint("active_days BETWEEN 1 AND 7", name="active_days_in_week"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    daily_xp: Mapped[int]  # XP on a typical day they practise
    active_days: Mapped[int]  # days a week they usually practise
    simulated_until: Mapped[datetime] = mapped_column(UTCDateTime)  # their XP is written up to here
