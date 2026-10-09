from datetime import date, datetime
from typing import Literal
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.course import CourseOut

DailyGoal = Literal[10, 20, 30, 50]


class HeartsOut(BaseModel):
    current: int = Field(description="Hearts right now, including any regenerated since they were spent.")
    max: int
    next_heart_at: datetime | None = Field(description="When the next heart comes back; null when full.")
    regen_minutes: int = Field(description="Minutes it takes to regenerate one heart.")


class StreakOut(BaseModel):
    length: int = Field(description="Current streak in days; 0 once a day has been missed.")
    extended_today: bool = Field(description="Whether today (in the learner's time zone) already counts.")
    longest: int = Field(description="Longest streak ever reached.")


class MeOut(BaseModel):
    """The logged-in learner with live stats."""

    id: int
    username: str
    display_name: str
    joined_at: datetime
    timezone: str = Field(description="IANA time zone; decides when the learner's day starts.")
    is_guest: bool = Field(
        description='Started over through "Get started" without a profile; the profile page asks for one.'
    )
    active_course: CourseOut | None
    daily_goal_xp: DailyGoal = Field(description="XP per day: 10 Casual, 20 Regular, 30 Serious, 50 Intense.")
    total_xp: int
    xp_today: int = Field(
        description="XP earned today in the learner's time zone; compare with daily_goal_xp."
    )
    lessons_completed: int = Field(
        description="Lessons and practice sessions finished so far, across all courses."
    )
    gems: int
    hearts: HeartsOut
    streak: StreakOut


class DailyXpOut(BaseModel):
    day: date = Field(description="A calendar day in the learner's time zone.")
    xp: int


def known_timezone(value: str) -> str:
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise ValueError("unknown IANA time zone") from exc
    return value


class MeUpdate(BaseModel):
    """Partial update: omitted (or null) fields are left unchanged."""

    model_config = ConfigDict(extra="forbid")

    active_course_id: int | None = Field(default=None, description="An available course's id.")
    daily_goal_xp: DailyGoal | None = None
    timezone: str | None = Field(
        default=None, max_length=64, description="IANA time zone name.", examples=["Asia/Kolkata"]
    )

    @field_validator("timezone")
    @classmethod
    def _known_timezone(cls, value: str | None) -> str | None:
        return value if value is None else known_timezone(value)


class Onboarding(BaseModel):
    """The choices made in the "Get started" flow. All are required."""

    model_config = ConfigDict(extra="forbid")

    active_course_id: int = Field(description="An available course's id.")
    daily_goal_xp: DailyGoal
    timezone: str = Field(
        max_length=64, description="IANA time zone name (the browser's).", examples=["Asia/Kolkata"]
    )

    @field_validator("timezone")
    @classmethod
    def _known_timezone(cls, value: str) -> str:
        return known_timezone(value)
