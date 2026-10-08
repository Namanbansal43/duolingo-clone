from datetime import datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.course import CourseOut

DailyGoal = Literal[10, 20, 30, 50]


class HeartsOut(BaseModel):
    current: int
    max: int
    next_heart_at: datetime | None
    regen_minutes: int


class StreakOut(BaseModel):
    length: int
    extended_today: bool
    longest: int


class MeOut(BaseModel):
    id: int
    username: str
    display_name: str
    joined_at: datetime
    timezone: str
    active_course: CourseOut | None
    daily_goal_xp: DailyGoal
    total_xp: int
    gems: int
    hearts: HeartsOut
    streak: StreakOut


class MeUpdate(BaseModel):
    """Partial update: omitted (or null) fields are left unchanged."""

    model_config = ConfigDict(extra="forbid")

    active_course_id: int | None = None
    daily_goal_xp: DailyGoal | None = None
    timezone: str | None = Field(default=None, max_length=64)

    @field_validator("timezone")
    @classmethod
    def _known_timezone(cls, value: str | None) -> str | None:
        if value is not None:
            try:
                ZoneInfo(value)
            except (ZoneInfoNotFoundError, ValueError) as exc:
                raise ValueError("unknown IANA time zone") from exc
        return value
