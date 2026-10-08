from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import Course, User
from app.schemas.me import MeUpdate


def update_learner(db: Session, user: User, changes: MeUpdate) -> None:
    """Apply the learner's own preferences (course, daily goal, time zone). Omitted fields are unchanged."""
    if changes.active_course_id is not None:
        course = db.get(Course, changes.active_course_id)
        if course is None:
            raise AppError(404, "course_not_found", "That course does not exist.")
        if not course.is_available:
            raise AppError(409, "course_unavailable", f"{course.title} is coming soon.")
        user.active_course = course

    if changes.daily_goal_xp is not None:
        user.daily_goal_xp = changes.daily_goal_xp

    if changes.timezone is not None:
        user.timezone = changes.timezone

    db.commit()
