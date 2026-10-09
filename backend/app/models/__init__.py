"""Importing this package registers every table on Base.metadata (Alembic relies on that)."""

from app.models.achievements import Achievement, AchievementMetric, AchievementTier, UserAchievement
from app.models.activity import LessonSession, SessionAnswer, SessionMode, SessionStatus, XpEvent, XpSource
from app.models.base import Base
from app.models.content import (
    AcceptedAnswer,
    Course,
    Exercise,
    ExerciseOption,
    ExerciseType,
    Lesson,
    Skill,
    SkillKind,
    Unit,
)
from app.models.leagues import League, LeagueMembership, Rival
from app.models.learner import DAILY_GOAL_OPTIONS, MAX_STREAK_FREEZES, User, UserSettings, UserSkillProgress

__all__ = [
    "DAILY_GOAL_OPTIONS",
    "MAX_STREAK_FREEZES",
    "AcceptedAnswer",
    "Achievement",
    "AchievementMetric",
    "AchievementTier",
    "Base",
    "Course",
    "Exercise",
    "ExerciseOption",
    "ExerciseType",
    "League",
    "LeagueMembership",
    "Lesson",
    "LessonSession",
    "Rival",
    "SessionAnswer",
    "SessionMode",
    "SessionStatus",
    "Skill",
    "SkillKind",
    "Unit",
    "User",
    "UserAchievement",
    "UserSettings",
    "UserSkillProgress",
    "XpEvent",
    "XpSource",
]
