from datetime import datetime

from pydantic import BaseModel, Field


class AchievementOut(BaseModel):
    key: str = Field(description='Stable code name, e.g. "wildfire".')
    title: str
    level: int = Field(description="Highest level reached; 0 before the first.")
    max_level: int
    value: int = Field(
        description="The learner's statistic: longest streak, total XP, lessons or perfect lessons."
    )
    goal: int = Field(
        description="What the next level needs; the last level's threshold once all are reached."
    )
    description: str = Field(description='The goal in words, e.g. "Reach a 7 day streak".')
    unlocked_at: datetime | None = Field(description="When the current level was reached; null at level 0.")
