from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Achievement, AchievementTier, Course, User, UserSettings
from app.seed import data


def seed_database(db: Session, *, default_username: str, now: datetime) -> None:
    """Insert whatever seed data is missing. Safe to run on every start: existing rows,
    including the learner's progress, are never overwritten."""
    _seed_courses(db)
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
            created_at=now,
            active_course=course,
            daily_goal_xp=data.DEFAULT_LEARNER_DAILY_GOAL_XP,
            gems=data.DEFAULT_LEARNER_GEMS,
            hearts_updated_at=now,
        )
        db.add(learner)
    if learner.settings is None:
        learner.settings = UserSettings()
