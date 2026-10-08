from fastapi import APIRouter

from app.deps import DbSession
from app.schemas.course import CatalogCourseOut, CourseOut
from app.services.courses import catalogue

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CatalogCourseOut])
def list_courses(db: DbSession) -> list[CatalogCourseOut]:
    """Every course in display order, with its learner count. Unavailable ones are shown as "coming soon"."""
    return [
        CatalogCourseOut(**CourseOut.model_validate(course).model_dump(), learners=learners)
        for course, learners in catalogue(db)
    ]
