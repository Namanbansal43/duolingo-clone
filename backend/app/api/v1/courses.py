from fastapi import APIRouter

from app.core.errors import error_response
from app.deps import CurrentUser, DbSession
from app.schemas.course import CatalogCourseOut, CourseOut
from app.schemas.path import PathNodeOut, PathOut, PathUnitOut
from app.services.courses import catalogue
from app.services.learner import available_course
from app.services.path import course_path

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CatalogCourseOut])
def list_courses(db: DbSession) -> list[CatalogCourseOut]:
    """Every course in display order, with its learner count. Unavailable ones are shown as "coming soon"."""
    return [
        CatalogCourseOut(**CourseOut.model_validate(course).model_dump(), learners=learners)
        for course, learners in catalogue(db)
    ]


@router.get(
    "/{course_id}/path",
    response_model=PathOut,
    responses={
        404: error_response("`course_not_found`: no course has that id."),
        409: error_response("`course_unavailable`: that course is coming soon."),
        422: error_response("`validation_error`: the id in the URL is not a whole number."),
        503: error_response("`learner_missing`: the default learner has not been seeded."),
    },
)
def get_path(course_id: int, user: CurrentUser, db: DbSession) -> PathOut:
    """The course's learning path for the learner: units, their nodes, and each node's state."""
    path = course_path(db, user, available_course(db, course_id))
    return PathOut(
        course=CourseOut.model_validate(path.course),
        units=[
            PathUnitOut(
                id=unit.id,
                position=unit.position,
                title=unit.title,
                nodes=[
                    PathNodeOut(
                        id=node.skill.id,
                        position=node.skill.position,
                        title=node.skill.title,
                        kind=node.skill.kind,
                        state=node.state,
                        lessons_total=node.lessons_total,
                        lessons_completed=node.lessons_completed,
                    )
                    for node in nodes
                ],
            )
            for unit, nodes in path.units
        ],
        active_node_id=path.active_skill_id,
    )
