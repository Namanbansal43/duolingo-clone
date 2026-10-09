from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LeagueOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int = Field(description="1 for Bronze up to 10 for Diamond.")
    name: str = Field(description='"Bronze"; shown as "Bronze League".')
    promotion_count: int = Field(description="The top N move up a league at the end of the week.")
    demotion_count: int = Field(description="The bottom N move down a league at the end of the week.")


class StandingOut(BaseModel):
    rank: int
    user_id: int
    display_name: str
    xp: int = Field(description="XP earned this league week.")
    is_me: bool


class WeekResultOut(BaseModel):
    week_start: date
    league: LeagueOut
    rank: int = Field(description="Final rank that week.")
    outcome: Literal["promoted", "stayed", "demoted"]
    next_league: LeagueOut = Field(description="The league that result leads to.")


class LeaderboardOut(BaseModel):
    unlocked: bool = Field(description="Leaderboards open after 10 finished lessons (practice included).")
    lessons_to_unlock: int = Field(description="Lessons left before leaderboards open; 0 once open.")
    sign_in_required: bool = Field(
        description='A guest from "Get started" who has finished 10 lessons: leagues need an account, so '
        "they are asked to sign in. Leaderboards stay locked for guests."
    )
    leagues: list[LeagueOut] = Field(description="All ten leagues, Bronze first.")
    league: LeagueOut | None = Field(
        description="This week's league: joined, or the one the next lesson joins. Null while locked."
    )
    joined: bool = Field(description="Whether a finished lesson has joined this week's league.")
    week_start: date = Field(description="The Monday this league week started, in the learner's time zone.")
    week_ends_at: datetime = Field(description="When this league week ends: the next Monday at midnight.")
    standings: list[StandingOut] = Field(description="The league by XP this week; empty until joined.")
    last_result: WeekResultOut | None = Field(description="How the learner's last finished week ended.")
    top_three_finishes: int
