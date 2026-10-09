from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Achievement,
    AchievementTier,
    Course,
    Lesson,
    LessonSession,
    SessionMode,
    SessionStatus,
    Skill,
    Unit,
    User,
    UserSettings,
    UserSkillProgress,
    XpEvent,
    XpSource,
)
from app.seed import data, spanish
from app.services.rules import LESSON_XP, STARTING_GEMS
from app.services.streak import local_date


def seed_database(db: Session, *, default_username: str, now: datetime) -> None:
    """Insert whatever seed data is missing. Safe to run on every start: existing rows,
    including the learner's progress, are never overwritten."""
    _seed_courses(db)
    _seed_spanish_content(db)
    _seed_achievements(db)
    _seed_default_learner(db, default_username, now)
    db.commit()


def _seed_courses(db: Session) -> None:
    existing = set(db.scalars(select(Course.learning_language).where(Course.from_language == "en")))
    for position, (code, title) in enumerate(data.COURSES):
        if code not in existing:
            db.add(
                Course(
                    learning_language=code,
                    from_language="en",
                    title=title,
                    position=position,
                    is_available=code in data.AVAILABLE_COURSES,
                )
            )
    db.flush()


def _seed_spanish_content(db: Session) -> None:
    """Units, path nodes and lessons, matched by position so reruns only add what is missing."""
    course = db.scalars(
        select(Course).where(Course.learning_language == "es", Course.from_language == "en")
    ).one()
    units = {unit.position: unit for unit in course.units}
    for unit_position, unit_seed in enumerate(spanish.UNITS, start=1):
        unit = units.get(unit_position)
        if unit is None:
            unit = Unit(position=unit_position, title=unit_seed.title)
            course.units.append(unit)
        skills = {skill.position: skill for skill in unit.skills}
        for skill_position, skill_seed in enumerate(unit_seed.skills, start=1):
            skill = skills.get(skill_position)
            if skill is None:
                skill = Skill(position=skill_position, title=skill_seed.title, kind=skill_seed.kind)
                unit.skills.append(skill)
            seeded = {lesson.position for lesson in skill.lessons}
            for lesson_position in range(1, skill_seed.lessons + 1):
                if lesson_position not in seeded:
                    skill.lessons.append(Lesson(position=lesson_position))
    db.flush()


def _seed_achievements(db: Session) -> None:
    existing = {achievement.key: achievement for achievement in db.scalars(select(Achievement))}
    for position, (key, title, description, metric, thresholds) in enumerate(data.ACHIEVEMENTS):
        achievement = existing.get(key)
        if achievement is None:
            achievement = Achievement(
                key=key, position=position, title=title, description=description, metric=metric
            )
            db.add(achievement)
        seeded_tiers = {tier.tier for tier in achievement.tiers}
        for tier, threshold in enumerate(thresholds, start=1):
            if tier not in seeded_tiers:
                achievement.tiers.append(AchievementTier(tier=tier, threshold=threshold))
    db.flush()


def _seed_default_learner(db: Session, username: str, now: datetime) -> None:
    learner = db.scalar(select(User).where(User.username == username))
    if learner is None:
        course = db.scalar(
            select(Course).where(
                Course.learning_language == data.DEFAULT_LEARNER_COURSE, Course.from_language == "en"
            )
        )
        learner = User(
            username=username,
            display_name=data.DEFAULT_LEARNER_NAME,
            created_at=now - timedelta(days=max(days for days, _ in data.DEMO_HISTORY)),
            active_course=course,
            daily_goal_xp=data.DEFAULT_LEARNER_DAILY_GOAL_XP,
            gems=STARTING_GEMS,
            hearts_updated_at=now,
        )
        db.add(learner)
        db.flush()
        _seed_demo_history(db, learner, now)
    if learner.settings is None:
        learner.settings = UserSettings()


def _seed_demo_history(db: Session, learner: User, now: datetime) -> None:
    """Finish the first few lessons of the learner's course on past days (data.DEMO_HISTORY), writing
    the same rows a real lesson would: a session, an XP event, path progress, XP total and streak."""
    lessons = db.scalars(
        select(Lesson)
        .join(Lesson.skill)
        .join(Skill.unit)
        .where(Unit.course_id == learner.active_course_id)
        .order_by(Unit.position, Skill.position, Lesson.position)
    ).all()
    days_ago_per_lesson = [days for days, count in data.DEMO_HISTORY for _ in range(count)]

    progress: dict[int, UserSkillProgress] = {}
    for index, (lesson, days_ago) in enumerate(zip(lessons, days_ago_per_lesson, strict=False)):
        finished_at = now - timedelta(days=days_ago) + timedelta(minutes=5 * index)
        session = LessonSession(
            user_id=learner.id,
            lesson=lesson,
            mode=SessionMode.LESSON,
            status=SessionStatus.COMPLETED,
            started_at=finished_at - timedelta(minutes=3),
            finished_at=finished_at,
            xp_earned=LESSON_XP,
        )
        db.add(session)
        db.add(
            XpEvent(
                user_id=learner.id,
                session=session,
                amount=LESSON_XP,
                source=XpSource.LESSON,
                earned_at=finished_at,
                local_date=local_date(finished_at, learner.timezone),
            )
        )
        skill_progress = progress.setdefault(
            lesson.skill_id,
            UserSkillProgress(user_id=learner.id, skill_id=lesson.skill_id, lessons_completed=0),
        )
        skill_progress.lessons_completed += 1
        if skill_progress.lessons_completed == len(lesson.skill.lessons):
            skill_progress.completed_at = finished_at
        learner.total_xp += LESSON_XP

    db.add_all(progress.values())
    learner.current_streak = learner.longest_streak = len(data.DEMO_HISTORY)
    learner.last_streak_date = local_date(
        now - timedelta(days=min(days for days, _ in data.DEMO_HISTORY)), learner.timezone
    )
