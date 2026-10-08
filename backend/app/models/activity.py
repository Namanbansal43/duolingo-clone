"""What learners did: lesson attempts, every answer, and every XP gain.

These rows are history. They are never edited after the fact, and the content they point at
cannot be deleted while they exist (ON DELETE RESTRICT).
"""

from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UTCDateTime, one_of
from app.models.content import Exercise, Lesson


class SessionMode(StrEnum):
    LESSON = "lesson"  # a new lesson: mistakes cost hearts
    PRACTICE = "practice"  # replaying finished material: no hearts lost


class SessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"  # ran out of hearts
    ABANDONED = "abandoned"  # quit part-way


class XpSource(StrEnum):
    LESSON = "lesson"
    PRACTICE = "practice"
    CHEST = "chest"
    ACHIEVEMENT = "achievement"


class LessonSession(Base):
    """One attempt at a lesson, from START to the result screen."""

    __tablename__ = "lesson_sessions"
    __table_args__ = (
        CheckConstraint(one_of("mode", SessionMode), name="mode_known"),
        CheckConstraint(one_of("status", SessionStatus), name="status_known"),
        # A session has a finish time exactly when it is no longer in progress.
        CheckConstraint(
            f"(status = '{SessionStatus.IN_PROGRESS}') = (finished_at IS NULL)",
            name="finished_matches_status",
        ),
        CheckConstraint("mistakes >= 0 AND xp_earned >= 0", name="counts_non_negative"),
        Index(None, "user_id", "started_at"),  # a learner's recent sessions
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lessons.id", ondelete="RESTRICT"))
    mode: Mapped[str] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(16), default=SessionStatus.IN_PROGRESS)
    started_at: Mapped[datetime] = mapped_column(UTCDateTime)
    finished_at: Mapped[datetime | None] = mapped_column(UTCDateTime)
    mistakes: Mapped[int] = mapped_column(default=0)
    xp_earned: Mapped[int] = mapped_column(default=0)

    lesson: Mapped[Lesson] = relationship()
    answers: Mapped[list["SessionAnswer"]] = relationship(
        back_populates="session",
        order_by="SessionAnswer.answered_at",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class SessionAnswer(Base):
    """Every answer submitted in a session, graded by the server. A wrong answer is asked again later
    in the same session, so one exercise can have several rows."""

    __tablename__ = "session_answers"
    __table_args__ = (Index(None, "session_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("lesson_sessions.id", ondelete="CASCADE"))
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id", ondelete="RESTRICT"))
    answer: Mapped[str] = mapped_column(Text)  # as submitted; structured answers are stored as JSON
    is_correct: Mapped[bool]
    answered_at: Mapped[datetime] = mapped_column(UTCDateTime)

    session: Mapped[LessonSession] = relationship(back_populates="answers")
    exercise: Mapped[Exercise] = relationship()


class XpEvent(Base):
    """One XP gain. This table is the source of truth for XP: the daily goal, the weekly leaderboard
    and the streak calendar are all sums over it, and users.total_xp is its running total."""

    __tablename__ = "xp_events"
    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_positive"),
        CheckConstraint(one_of("source", XpSource), name="source_known"),
        Index(None, "user_id", "local_date"),  # one learner's XP per day: daily goal, calendar
        Index(None, "local_date"),  # everyone's XP in a date range: the weekly leaderboard
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    session_id: Mapped[int | None] = mapped_column(ForeignKey("lesson_sessions.id", ondelete="SET NULL"))
    amount: Mapped[int]
    source: Mapped[str] = mapped_column(String(16))
    earned_at: Mapped[datetime] = mapped_column(UTCDateTime)
    local_date: Mapped[date]  # the learner's calendar date when it was earned

    session: Mapped[LessonSession | None] = relationship()
