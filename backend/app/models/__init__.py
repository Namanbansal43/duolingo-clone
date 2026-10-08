"""Importing this package registers every table on Base.metadata (Alembic relies on that)."""

from app.models.base import Base
from app.models.content import Course
from app.models.learner import DAILY_GOAL_OPTIONS, User

__all__ = ["DAILY_GOAL_OPTIONS", "Base", "Course", "User"]
