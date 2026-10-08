from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.course import CourseOut


class PathNodeOut(BaseModel):
    id: int = Field(description="The skill (path node) id.")
    position: int
    title: str
    kind: Literal["lesson", "chest", "review"] = Field(
        description="Star node, treasure chest, or unit-review trophy."
    )
    state: Literal["completed", "active", "locked"]
    lessons_total: int = Field(description="Lessons in this node; 0 for a chest.")
    lessons_completed: int = Field(description="Lessons finished so far; drives the progress ring.")


class PathUnitOut(BaseModel):
    id: int
    position: int = Field(description="Unit number within the course, from 1.")
    title: str
    nodes: list[PathNodeOut]


class PathOut(BaseModel):
    course: CourseOut
    units: list[PathUnitOut]
    active_node_id: int | None = Field(description="The node to play next; null once the course is finished.")


class ChestOut(BaseModel):
    gems_awarded: int
    gems: int = Field(description="The learner's gem balance after opening.")
