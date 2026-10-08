from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Course, User


def catalogue(db: Session) -> list[tuple[Course, int]]:
    """Every course in display order, paired with the number of learners studying it."""
    learners = (
        select(User.active_course_id, func.count().label("learners"))
        .group_by(User.active_course_id)
        .subquery()
    )
    rows = db.execute(
        select(Course, func.coalesce(learners.c.learners, 0))
        .outerjoin(learners, learners.c.active_course_id == Course.id)
        .order_by(Course.position)
    )
    return [(course, count) for course, count in rows]
