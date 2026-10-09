from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.me import HeartsOut

ExerciseKind = Literal["multiple_choice", "word_bank", "match_pairs", "fill_blank", "type_answer", "listen"]


class SessionStart(BaseModel):
    model_config = ConfigDict(extra="forbid")

    skill_id: int = Field(
        description="The path node to play: the active one (a lesson) or a completed one (practice)."
    )


class OptionOut(BaseModel):
    id: int
    text: str


class MatchTilesOut(BaseModel):
    left: list[str] = Field(description="English tiles, shuffled.")
    right: list[str] = Field(description="Spanish tiles, shuffled separately.")


class ExerciseOut(BaseModel):
    """One challenge, without its solution."""

    id: int
    type: ExerciseKind
    instruction: str = Field(examples=["Write this in English"])
    prompt: str | None = Field(
        description="The sentence or word to work on; for fill_blank it contains ___. Null for match_pairs."
    )
    prompt_language: str | None = Field(description="Language of the prompt; also picks the voice for audio.")
    options: list[OptionOut] = Field(
        description="Choices (multiple_choice, fill_blank) or word tiles (word_bank, listen), shuffled. "
        "Empty for type_answer and match_pairs."
    )
    pairs: MatchTilesOut | None = Field(description="match_pairs only.")


class SessionNodeOut(BaseModel):
    id: int
    title: str


class SessionOut(BaseModel):
    """A lesson (or practice) session in progress, with everything needed to play or resume it."""

    id: int
    mode: Literal["lesson", "practice"] = Field(
        description="Practice replays a completed node: no hearts lost."
    )
    status: Literal["in_progress", "completed", "failed", "abandoned"]
    started_at: datetime
    node: SessionNodeOut
    lesson_position: int = Field(description="Which lesson of the node this is, from 1.")
    lessons_total: int
    exercises: list[ExerciseOut]
    completed_exercise_ids: list[int] = Field(
        description="Exercises already answered correctly in this session."
    )
    hearts: HeartsOut


class AnswerIn(BaseModel):
    """One answer. Which field to send depends on the exercise type."""

    model_config = ConfigDict(extra="forbid")

    exercise_id: int
    option_ids: list[int] | None = Field(
        default=None,
        description="multiple_choice and fill_blank: the chosen option. "
        "word_bank and listen: the tiles, in order.",
    )
    text: str | None = Field(default=None, max_length=500, description="type_answer: what was typed.")
    pair: tuple[str, str] | None = Field(
        default=None, description="match_pairs: one attempted pair, [left tile, right tile]."
    )
    skipped: bool = Field(
        default=False, description="SKIP: counts as a wrong answer and reveals the solution."
    )


class AnswerOut(BaseModel):
    correct: bool
    verdict: Literal["correct", "other_solution", "typo", "wrong"] = Field(
        description="other_solution: right, but the main translation differs. typo: right apart from a slip."
    )
    solution: str | None = Field(
        description="Shown in the feedback bar: the correct solution (wrong), the main translation "
        "(other_solution) or the right spelling (typo). Null otherwise."
    )
    exercise_completed: bool = Field(
        description="False only for a match_pairs exercise with pairs left to match."
    )
    hearts: HeartsOut


class StreakChangeOut(BaseModel):
    length: int
    longest: int
    extended: bool = Field(description="This session was the first to count today, so the streak grew.")


class NodeProgressOut(BaseModel):
    id: int
    lessons_completed: int
    lessons_total: int
    completed: bool


class CompletionOut(BaseModel):
    xp_earned: int
    total_xp: int
    xp_today: int
    daily_goal_xp: int
    accuracy: int = Field(description="Percent of exercises answered right the first time.")
    duration_seconds: int
    streak: StreakChangeOut
    hearts: HeartsOut
    node: NodeProgressOut
