from fastapi import APIRouter
from sqlalchemy import select

from app.deps import DbSession
from app.models import Course
from app.schemas.course import CourseOut

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseOut])
def list_courses(db: DbSession) -> list[Course]:
    """Every course, in display order. Unavailable ones are shown as "coming soon"."""
    return list(db.scalars(select(Course).order_by(Course.position)))
