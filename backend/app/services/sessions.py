"""Lesson sessions: starting a lesson, grading every answer, and what finishing one earns.

The server decides everything that matters: which lesson is next, whether an answer is right, how many
hearts are left, and the XP, streak and path progress a finished lesson brings. The client only plays it.
"""

import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.models import (
    Course,
    Exercise,
    ExerciseOption,
    ExerciseType,
    Lesson,
    LessonSession,
    SessionAnswer,
    SessionMode,
    SessionStatus,
    Skill,
    SkillKind,
    User,
    UserSkillProgress,
    XpEvent,
    XpSource,
)
from app.schemas.session import AnswerIn
from app.services.achievements import AchievementProgress, unlock_achievements
from app.services.grading import Grade, Verdict, grade_text
from app.services.hearts import add_hearts, live_hearts
from app.services.leagues import join_league
from app.services.path import NodeState, path_node
from app.services.rules import LESSON_XP, PRACTICE_HEARTS, PRACTICE_XP
from app.services.streak import extend_streak, local_date

LANGUAGE_NAMES = {"en": "English"}  # languages courses are taught in; course titles name the others

# "Can't listen now" skips listening exercises, so a lesson can be finished without them.
SKIPPABLE = {ExerciseType.LISTEN}


@dataclass(frozen=True)
class AnswerResult:
    grade: Grade
    exercise_completed: bool


@dataclass(frozen=True)
class Completion:
    xp_earned: int
    accuracy: int
    duration_seconds: int
    streak_extended: bool
    lessons_completed: int
    lessons_total: int
    node_completed: bool
    achievements: list[AchievementProgress]  # those that went up a level
    leaderboard_unlocked: bool  # this session made the learner's 10th: they entered the Bronze League


def start_session(
    db: Session, user: User, skill_id: int, now: datetime, regen_every: timedelta
) -> LessonSession:
    """Start the next lesson of the active node, or practice a completed one."""
    skill = db.get(Skill, skill_id)
    if skill is None:
        raise AppError(404, "skill_not_found", "That path node does not exist.")
    if skill.kind == SkillKind.CHEST:
        raise AppError(409, "not_a_lesson", "Treasure chests are opened, not played.")
    node = path_node(db, user, skill)
    if node.state == NodeState.LOCKED:
        raise AppError(409, "skill_locked", "Complete the levels above to unlock this.")

    if not skill.lessons:
        raise AppError(409, "lesson_unavailable", "This lesson is coming soon.")
    if node.state == NodeState.ACTIVE:
        mode = SessionMode.LESSON
        lesson = skill.lessons[min(node.lessons_completed, len(skill.lessons) - 1)]
    else:  # a completed node: practice its lessons in turn
        mode = SessionMode.PRACTICE
        lesson = skill.lessons[_practice_count(db, user, skill) % len(skill.lessons)]
    if not lesson.exercises:
        raise AppError(409, "lesson_unavailable", "This lesson is coming soon.")
    if mode == SessionMode.LESSON and live_hearts(user, now, regen_every).current == 0:
        raise AppError(409, "out_of_hearts", "You have no hearts left.")

    # One session at a time: anything left unfinished is abandoned.
    db.execute(
        update(LessonSession)
        .where(LessonSession.user_id == user.id, LessonSession.status == SessionStatus.IN_PROGRESS)
        .values(status=SessionStatus.ABANDONED, finished_at=now)
    )
    session = LessonSession(
        user_id=user.id, lesson=lesson, mode=mode, status=SessionStatus.IN_PROGRESS, started_at=now
    )
    db.add(session)
    db.commit()
    return session


def current_session(db: Session, user: User) -> LessonSession:
    """The learner's unfinished session (there is at most one: starting another abandons it)."""
    session = db.scalar(
        select(LessonSession)
        .where(LessonSession.user_id == user.id, LessonSession.status == SessionStatus.IN_PROGRESS)
        .order_by(LessonSession.started_at.desc(), LessonSession.id.desc())
    )
    if session is None:
        raise AppError(404, "session_not_found", "No lesson is in progress.")
    return session


def get_session(db: Session, user: User, session_id: int) -> LessonSession:
    session = db.get(LessonSession, session_id)
    if session is None or session.user_id != user.id:
        raise AppError(404, "session_not_found", "That lesson session does not exist.")
    return session


def completed_exercise_ids(session: LessonSession) -> list[int]:
    answers = _answers_by_exercise(session)
    return [
        exercise.id
        for exercise in session.lesson.exercises
        if _is_done(exercise, answers.get(exercise.id, []))
    ]


def submit_answer(
    db: Session, user: User, session: LessonSession, answer: AnswerIn, now: datetime, regen_every: timedelta
) -> AnswerResult:
    """Grade one answer. In a lesson a wrong answer costs a heart; in practice nothing is lost."""
    _require_in_progress(session)
    exercise = next((e for e in session.lesson.exercises if e.id == answer.exercise_id), None)
    if exercise is None:
        raise AppError(404, "exercise_not_found", "That exercise is not part of this session.")
    answers = _answers_by_exercise(session)
    if _is_done(exercise, answers.get(exercise.id, [])):
        raise AppError(409, "exercise_completed", "That exercise has already been answered.")
    if session.mode == SessionMode.LESSON and live_hearts(user, now, regen_every).current == 0:
        raise AppError(409, "out_of_hearts", "You have no hearts left.")

    grade, submitted = _grade(exercise, answer)
    row = SessionAnswer(
        exercise=exercise, answer=json.dumps(submitted), is_correct=grade.correct, answered_at=now
    )
    session.answers.append(row)
    if not grade.correct:
        session.mistakes += 1
        if session.mode == SessionMode.LESSON:
            add_hearts(user, -1, now, regen_every)
    db.commit()
    return AnswerResult(
        grade=grade, exercise_completed=_is_done(exercise, [*answers.get(exercise.id, []), row])
    )


def complete_session(
    db: Session, user: User, session: LessonSession, now: datetime, regen_every: timedelta
) -> Completion:
    """Finish a session whose exercises are all answered: XP, streak, path progress (a lesson) or a heart
    (practice), any achievement levels this reaches, and a place in this week's league."""
    _require_in_progress(session)
    answers = _answers_by_exercise(session)
    if any(
        not _is_done(exercise, answers.get(exercise.id, []))
        for exercise in session.lesson.exercises
        if exercise.type not in SKIPPABLE
    ):
        raise AppError(409, "session_incomplete", "Answer every exercise before finishing the lesson.")

    is_lesson = session.mode == SessionMode.LESSON
    xp = LESSON_XP if is_lesson else PRACTICE_XP
    today = local_date(now, user.timezone)
    session.status = SessionStatus.COMPLETED
    session.finished_at = now
    session.xp_earned = xp
    db.add(
        XpEvent(
            user_id=user.id,
            session=session,
            amount=xp,
            source=XpSource.LESSON if is_lesson else XpSource.PRACTICE,
            earned_at=now,
            local_date=today,
        )
    )
    user.total_xp += xp

    streak = extend_streak(
        current=user.current_streak, longest=user.longest_streak, last_date=user.last_streak_date, today=today
    )
    user.current_streak, user.longest_streak, user.last_streak_date = (
        streak.current,
        streak.longest,
        streak.last_date,
    )

    skill = session.lesson.skill
    progress = db.get(UserSkillProgress, (user.id, skill.id))
    if progress is None:
        progress = UserSkillProgress(user_id=user.id, skill_id=skill.id, lessons_completed=0)
        db.add(progress)
    if is_lesson:
        # Only the node's next lesson moves it forward (a stale session for an earlier lesson doesn't).
        if progress.completed_at is None and session.lesson.position == progress.lessons_completed + 1:
            progress.lessons_completed += 1
            if progress.lessons_completed >= len(skill.lessons):
                progress.completed_at = now
    else:
        add_hearts(user, PRACTICE_HEARTS, now, regen_every)

    achievements = unlock_achievements(db, user, now)
    leaderboard_unlocked = join_league(db, user, now)
    db.commit()
    return Completion(
        xp_earned=xp,
        accuracy=_accuracy(session.lesson.exercises, answers),
        duration_seconds=int((now - session.started_at).total_seconds()),
        streak_extended=streak.extended,
        lessons_completed=progress.lessons_completed,
        lessons_total=len(skill.lessons),
        node_completed=progress.completed_at is not None,
        achievements=achievements,
        leaderboard_unlocked=leaderboard_unlocked,
    )


def quit_session(
    db: Session, user: User, session: LessonSession, now: datetime, regen_every: timedelta
) -> None:
    """Leave a session early: it failed if hearts ran out in a lesson, otherwise it was abandoned."""
    _require_in_progress(session)
    out_of_hearts = session.mode == SessionMode.LESSON and live_hearts(user, now, regen_every).current == 0
    session.status = SessionStatus.FAILED if out_of_hearts else SessionStatus.ABANDONED
    session.finished_at = now
    db.commit()


def instruction(exercise: Exercise, course: Course) -> str:
    """The heading above an exercise, e.g. "Write this in English"."""
    into = LANGUAGE_NAMES.get(course.from_language, course.from_language)
    if exercise.prompt_language == course.from_language:
        into = course.title
    match exercise.type:
        case ExerciseType.MULTIPLE_CHOICE:
            return "Select the correct meaning"
        case ExerciseType.WORD_BANK | ExerciseType.TYPE_ANSWER:
            return f"Write this in {into}"
        case ExerciseType.MATCH_PAIRS:
            return "Select the matching pairs"
        case ExerciseType.FILL_BLANK:
            return "Fill in the blank"
        case _:
            return "Tap what you hear"


def shuffled[T](items: list[T], session: LessonSession, exercise: Exercise, salt: str = "") -> list[T]:
    """The same order every time a session is loaded, so a refresh doesn't move the tiles around."""
    items = list(items)
    random.Random(f"{session.id}-{exercise.id}-{salt}").shuffle(items)
    return items


def _practice_count(db: Session, user: User, skill: Skill) -> int:
    return db.scalar(
        select(func.count())
        .select_from(LessonSession)
        .join(Lesson, Lesson.id == LessonSession.lesson_id)
        .where(
            LessonSession.user_id == user.id,
            LessonSession.mode == SessionMode.PRACTICE,
            LessonSession.status == SessionStatus.COMPLETED,
            Lesson.skill_id == skill.id,
        )
    )


def _require_in_progress(session: LessonSession) -> None:
    if session.status != SessionStatus.IN_PROGRESS:
        raise AppError(409, "session_finished", "That lesson session has already ended.")


def _answers_by_exercise(session: LessonSession) -> dict[int, list[SessionAnswer]]:
    grouped: dict[int, list[SessionAnswer]] = {}
    for row in sorted(session.answers, key=lambda row: (row.answered_at, row.id or 0)):
        grouped.setdefault(row.exercise_id, []).append(row)
    return grouped


def _is_done(exercise: Exercise, answers: list[SessionAnswer]) -> bool:
    if exercise.type == ExerciseType.MATCH_PAIRS:
        matched = {row.answer for row in answers if row.is_correct}
        return len(matched) == len(exercise.options)
    return any(row.is_correct for row in answers)


def _accuracy(exercises: list[Exercise], answers: dict[int, list[SessionAnswer]]) -> int:
    """Percent of answered exercises that were right the first time (all pairs, for match_pairs)."""
    answered = [answers[e.id] for e in exercises if answers.get(e.id)]
    if not answered:
        return 100
    first_time = sum(
        all(row.is_correct for row in rows)
        if exercise.type == ExerciseType.MATCH_PAIRS
        else rows[0].is_correct
        for exercise, rows in ((e, answers[e.id]) for e in exercises if answers.get(e.id))
    )
    return round(100 * first_time / len(answered))


def _grade(exercise: Exercise, answer: AnswerIn) -> tuple[Grade, dict]:
    """Grade an answer and return it with what is stored for it."""
    if answer.skipped:
        return Grade(Verdict.WRONG, _solution(exercise)), {"skipped": True}

    kind = exercise.type
    if kind in (ExerciseType.MULTIPLE_CHOICE, ExerciseType.FILL_BLANK):
        (option,) = _options(exercise, answer, exactly_one=True)
        grade = (
            Grade(Verdict.CORRECT, None) if option.is_correct else Grade(Verdict.WRONG, _solution(exercise))
        )
        return grade, {"option_ids": [option.id]}

    if kind in (ExerciseType.WORD_BANK, ExerciseType.LISTEN):
        tiles = _options(exercise, answer, exactly_one=False)
        text = " ".join(tile.text for tile in tiles)
        return _grade_written(exercise, text, lenient=False), {"option_ids": [tile.id for tile in tiles]}

    if kind == ExerciseType.TYPE_ANSWER:
        if answer.text is None or answer.option_ids is not None or answer.pair is not None:
            raise AppError(422, "invalid_answer", "Send the typed answer as text.")
        return _grade_written(exercise, answer.text, lenient=True), {"text": answer.text}

    # match_pairs: one attempted pair at a time, left (English) to right (Spanish).
    if answer.pair is None or answer.option_ids is not None or answer.text is not None:
        raise AppError(422, "invalid_answer", "Send the attempted pair as pair: [left, right].")
    left, right = answer.pair
    if not any(o.match_text == left for o in exercise.options) or not any(
        o.text == right for o in exercise.options
    ):
        raise AppError(422, "invalid_answer", "Both tiles must belong to this exercise.")
    correct = any(o.match_text == left and o.text == right for o in exercise.options)
    return Grade(Verdict.CORRECT if correct else Verdict.WRONG, None), {"pair": [left, right]}


def _options(exercise: Exercise, answer: AnswerIn, *, exactly_one: bool) -> list[ExerciseOption]:
    ids = answer.option_ids
    if ids is None or answer.text is not None or answer.pair is not None:
        raise AppError(422, "invalid_answer", "Send the chosen options as option_ids.")
    if (exactly_one and len(ids) != 1) or not ids or len(set(ids)) != len(ids):
        raise AppError(
            422, "invalid_answer", "Choose one option." if exactly_one else "Use each tile at most once."
        )
    by_id = {option.id: option for option in exercise.options}
    if any(option_id not in by_id for option_id in ids):
        raise AppError(422, "invalid_answer", "Those options don't belong to this exercise.")
    return [by_id[option_id] for option_id in ids]


def _grade_written(exercise: Exercise, text: str, *, lenient: bool) -> Grade:
    accepted = [row.text for row in exercise.accepted_answers]
    return grade_text(text, accepted, _primary(exercise), lenient=lenient)


def _primary(exercise: Exercise) -> str:
    return next(row.text for row in exercise.accepted_answers if row.is_primary)


def _solution(exercise: Exercise) -> str | None:
    """What "Correct solution:" shows when an answer is wrong."""
    match exercise.type:
        case ExerciseType.MULTIPLE_CHOICE:
            return next(o.text for o in exercise.options if o.is_correct)
        case ExerciseType.FILL_BLANK:
            return (exercise.prompt or "").replace(
                "___", next(o.text for o in exercise.options if o.is_correct)
            )
        case ExerciseType.MATCH_PAIRS:
            return None
        case _:
            return _primary(exercise)
