from fastapi import APIRouter, Response, status

from app.api.v1.views import achievement_out, hearts_out, regen_every
from app.core.clock import Clock
from app.core.config import Settings
from app.core.errors import error_response
from app.deps import ClockDep, CurrentUser, DbSession, SettingsDep
from app.models import Course, Exercise, ExerciseType, LessonSession, User
from app.schemas.session import (
    AnswerIn,
    AnswerOut,
    CompletionOut,
    ExerciseOut,
    MatchTilesOut,
    NodeProgressOut,
    OptionOut,
    SessionNodeOut,
    SessionOut,
    SessionStart,
    StreakChangeOut,
)
from app.services import sessions as service
from app.services.learner import xp_earned_on
from app.services.streak import local_date

router = APIRouter(
    prefix="/sessions",
    tags=["sessions"],
    responses={503: error_response("`learner_missing`: the default learner has not been seeded.")},
)

NOT_FOUND = error_response("`session_not_found`: no session of this learner has that id.")
INVALID_ID = error_response("`validation_error`: the id in the URL is not a whole number.")


@router.post(
    "",
    response_model=SessionOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        404: error_response("`skill_not_found`: no path node has that id."),
        409: error_response(
            "`skill_locked`, `not_a_lesson` (a chest), `lesson_unavailable` (no exercises yet) "
            "or `out_of_hearts` (a lesson needs at least one heart)."
        ),
        422: error_response("`validation_error`: `skill_id` is missing or not a whole number."),
    },
)
def start_session(
    body: SessionStart, user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep
) -> SessionOut:
    """Start the next lesson of the active path node, or practice a completed node (no hearts at stake).
    Any other unfinished session of the learner is abandoned."""
    session = service.start_session(db, user, body.skill_id, clock.now(), regen_every(settings))
    return _session_out(session, user, clock, settings)


@router.get(
    "/current",
    response_model=SessionOut,
    responses={404: error_response("`session_not_found`: no lesson is in progress.")},
)
def get_current_session(
    user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep
) -> SessionOut:
    """The session in progress, if any. The lesson page plays this one, so a refresh resumes it."""
    return _session_out(service.current_session(db, user), user, clock, settings)


@router.get("/{session_id}", response_model=SessionOut, responses={404: NOT_FOUND, 422: INVALID_ID})
def get_session(
    session_id: int, user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep
) -> SessionOut:
    """A session with its exercises and what has been answered so far, to play it or pick it up again."""
    return _session_out(service.get_session(db, user, session_id), user, clock, settings)


@router.post(
    "/{session_id}/answers",
    response_model=AnswerOut,
    responses={
        404: error_response("`session_not_found`, or `exercise_not_found` (not part of this session)."),
        409: error_response(
            "`session_finished`, `exercise_completed` (already answered) or `out_of_hearts`."
        ),
        422: error_response("`invalid_answer`: the wrong field for this exercise type, or unknown options."),
    },
)
def answer_exercise(
    session_id: int, body: AnswerIn, user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep
) -> AnswerOut:
    """Grade one answer on the server. In a lesson a wrong answer (or SKIP) costs a heart; match_pairs
    is answered one attempted pair at a time, and a wrong pair costs a heart too."""
    session = service.get_session(db, user, session_id)
    result = service.submit_answer(db, user, session, body, clock.now(), regen_every(settings))
    return AnswerOut(
        correct=result.grade.correct,
        verdict=result.grade.verdict,
        solution=result.grade.solution,
        exercise_completed=result.exercise_completed,
        hearts=hearts_out(user, clock.now(), settings),
    )


@router.post(
    "/{session_id}/complete",
    response_model=CompletionOut,
    responses={
        404: NOT_FOUND,
        409: error_response("`session_finished`, or `session_incomplete` (exercises left to answer)."),
        422: INVALID_ID,
    },
)
def complete_session(
    session_id: int, user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep
) -> CompletionOut:
    """Finish a session: award XP, extend the streak, and move the path node on (a lesson) or give back
    a heart (practice). Lists any achievements that went up a level."""
    session = service.get_session(db, user, session_id)
    done = service.complete_session(db, user, session, clock.now(), regen_every(settings))
    return CompletionOut(
        xp_earned=done.xp_earned,
        total_xp=user.total_xp,
        xp_today=xp_earned_on(db, user, local_date(clock.now(), user.timezone)),
        daily_goal_xp=user.daily_goal_xp,
        accuracy=done.accuracy,
        duration_seconds=done.duration_seconds,
        streak=StreakChangeOut(
            length=user.current_streak, longest=user.longest_streak, extended=done.streak_extended
        ),
        hearts=hearts_out(user, clock.now(), settings),
        node=NodeProgressOut(
            id=session.lesson.skill_id,
            lessons_completed=done.lessons_completed,
            lessons_total=done.lessons_total,
            completed=done.node_completed,
        ),
        achievements=[achievement_out(progress) for progress in done.achievements],
    )


@router.post(
    "/{session_id}/quit",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: NOT_FOUND, 409: error_response("`session_finished`."), 422: INVALID_ID},
)
def quit_session(
    session_id: int, user: CurrentUser, db: DbSession, clock: ClockDep, settings: SettingsDep
) -> Response:
    """Leave a session early. It counts as failed if the learner ran out of hearts, abandoned otherwise."""
    session = service.get_session(db, user, session_id)
    service.quit_session(db, user, session, clock.now(), regen_every(settings))
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _session_out(session: LessonSession, user: User, clock: Clock, settings: Settings) -> SessionOut:
    lesson = session.lesson
    course = lesson.skill.unit.course
    return SessionOut(
        id=session.id,
        mode=session.mode,
        status=session.status,
        started_at=session.started_at,
        node=SessionNodeOut(id=lesson.skill.id, title=lesson.skill.title),
        lesson_position=lesson.position,
        lessons_total=len(lesson.skill.lessons),
        exercises=[_exercise_out(session, exercise, course) for exercise in lesson.exercises],
        completed_exercise_ids=service.completed_exercise_ids(session),
        hearts=hearts_out(user, clock.now(), settings),
    )


def _exercise_out(session: LessonSession, exercise: Exercise, course: Course) -> ExerciseOut:
    is_match = exercise.type == ExerciseType.MATCH_PAIRS
    options = [] if is_match else [OptionOut(id=o.id, text=o.text) for o in exercise.options]
    return ExerciseOut(
        id=exercise.id,
        type=exercise.type,
        instruction=service.instruction(exercise, course),
        prompt=exercise.prompt,
        prompt_language=exercise.prompt_language,
        options=service.shuffled(options, session, exercise),
        pairs=MatchTilesOut(
            left=service.shuffled([o.match_text or "" for o in exercise.options], session, exercise, "left"),
            right=service.shuffled([o.text for o in exercise.options], session, exercise, "right"),
        )
        if is_match
        else None,
    )
