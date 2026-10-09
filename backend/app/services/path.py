"""The learning path: which nodes are done, which one is next, and what is still locked."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.models import Course, Lesson, Skill, SkillKind, Unit, User, UserSkillProgress
from app.services.rules import CHEST_GEMS


class NodeState(StrEnum):
    COMPLETED = "completed"
    ACTIVE = "active"  # the next node to play; exactly one per course until everything is done
    LOCKED = "locked"


@dataclass(frozen=True)
class PathNode:
    skill: Skill
    state: NodeState
    lessons_total: int
    lessons_completed: int


@dataclass(frozen=True)
class CoursePath:
    course: Course
    units: list[tuple[Unit, list[PathNode]]]
    active_skill_id: int | None


def course_path(db: Session, user: User, course: Course) -> CoursePath:
    """Nodes unlock strictly in order: everything before the first unfinished node is completed, that node is
    active, and everything after it is locked. Only completion is stored; the states are derived here."""
    units = db.scalars(
        select(Unit)
        .where(Unit.course_id == course.id)
        .order_by(Unit.position)
        .options(selectinload(Unit.skills))
    ).all()
    lesson_counts = dict(
        db.execute(
            select(Lesson.skill_id, func.count())
            .join(Lesson.skill)
            .join(Skill.unit)
            .where(Unit.course_id == course.id)
            .group_by(Lesson.skill_id)
        ).all()
    )
    progress = {
        row.skill_id: row
        for row in db.scalars(
            select(UserSkillProgress)
            .join(Skill, Skill.id == UserSkillProgress.skill_id)
            .join(Skill.unit)
            .where(UserSkillProgress.user_id == user.id, Unit.course_id == course.id)
        )
    }

    active_skill_id: int | None = None
    path_units = []
    for unit in units:
        nodes = []
        for skill in unit.skills:
            done = progress.get(skill.id)
            if done is not None and done.completed_at is not None:
                state = NodeState.COMPLETED
            elif active_skill_id is None:
                state = NodeState.ACTIVE
                active_skill_id = skill.id
            else:
                state = NodeState.LOCKED
            nodes.append(
                PathNode(
                    skill=skill,
                    state=state,
                    lessons_total=lesson_counts.get(skill.id, 0),
                    lessons_completed=done.lessons_completed if done else 0,
                )
            )
        path_units.append((unit, nodes))
    return CoursePath(course=course, units=path_units, active_skill_id=active_skill_id)


def path_node(db: Session, user: User, skill: Skill) -> PathNode:
    """One node of the learner's path, with its state."""
    return next(
        node
        for _, nodes in course_path(db, user, skill.unit.course).units
        for node in nodes
        if node.skill.id == skill.id
    )


def open_chest(db: Session, user: User, skill_id: int, now: datetime) -> int:
    """Open the chest node the learner has reached and pay out its gems. Returns the gems awarded."""
    skill = db.get(Skill, skill_id)
    if skill is None:
        raise AppError(404, "skill_not_found", "That path node does not exist.")
    if skill.kind != SkillKind.CHEST:
        raise AppError(409, "not_a_chest", "That path node is not a chest.")

    node = path_node(db, user, skill)
    if node.state == NodeState.COMPLETED:
        raise AppError(409, "chest_already_opened", "That chest has already been opened.")
    if node.state == NodeState.LOCKED:
        raise AppError(409, "skill_locked", "Complete the levels above to reach this chest.")

    progress = db.get(UserSkillProgress, (user.id, skill.id))
    if progress is None:
        progress = UserSkillProgress(user_id=user.id, skill_id=skill.id, lessons_completed=0)
        db.add(progress)
    progress.completed_at = now
    user.gems += CHEST_GEMS
    db.commit()
    return CHEST_GEMS
