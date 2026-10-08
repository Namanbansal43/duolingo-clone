from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Course, LessonSession, SessionStatus, User, XpEvent
from app.schemas.me import MeUpdate


def available_course(db: Session, course_id: int) -> Course:
    """The course with this id, if learners can study it; otherwise a 404 or 409 error."""
    course = db.get(Course, course_id)
    if course is None:
        raise AppError(404, "course_not_found", "That course does not exist.")
    if not course.is_available:
        raise AppError(409, "course_unavailable", f"{course.title} is coming soon.")
    return course


def update_learner(db: Session, user: User, changes: MeUpdate) -> None:
    """Apply the learner's own preferences (course, daily goal, time zone). Omitted fields are unchanged."""
    if changes.active_course_id is not None:
        user.active_course = available_course(db, changes.active_course_id)

    if changes.daily_goal_xp is not None:
        user.daily_goal_xp = changes.daily_goal_xp

    if changes.timezone is not None:
        user.timezone = changes.timezone

    db.commit()


def xp_earned_on(db: Session, user: User, day: date) -> int:
    """XP earned on one of the learner's calendar days (the daily goal compares against this)."""
    total = db.scalar(
        select(func.sum(XpEvent.amount)).where(XpEvent.user_id == user.id, XpEvent.local_date == day)
    )
    return total or 0


def lessons_completed(db: Session, user: User) -> int:
    return db.scalar(
        select(func.count())
        .select_from(LessonSession)
        .where(LessonSession.user_id == user.id, LessonSession.status == SessionStatus.COMPLETED)
    )
