"""Rules the database itself enforces, whatever the application code does."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.orm import Session

from app.models import (
    AcceptedAnswer,
    Achievement,
    Base,
    Exercise,
    ExerciseOption,
    ExerciseType,
    League,
    LeagueMembership,
    Lesson,
    LessonSession,
    Rival,
    SessionAnswer,
    SessionMode,
    SessionStatus,
    Unit,
    User,
    UserAchievement,
    UserSettings,
    UserSkillProgress,
    XpEvent,
    XpSource,
)
from tests.conftest import NOW


def count(db: Session, model: type[Base]) -> int:
    return db.scalar(select(func.count()).select_from(model))


def finished_session(lesson: Lesson, user: User) -> LessonSession:
    return LessonSession(
        user_id=user.id,
        lesson=lesson,
        mode=SessionMode.LESSON,
        status=SessionStatus.COMPLETED,
        started_at=NOW - timedelta(minutes=3),
        finished_at=NOW,
        xp_earned=10,
    )


# Learner state


def test_foreign_keys_are_enforced(db: Session, learner: User) -> None:
    learner.active_course_id = 9999
    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        db.commit()


@pytest.mark.parametrize(
    ("column", "value"),
    [("hearts", 6), ("gems", -1), ("daily_goal_xp", 15), ("longest_streak", -1), ("streak_freezes", 3)],
)
def test_learner_state_stays_in_range(db: Session, learner: User, column: str, value: int) -> None:
    setattr(learner, column, value)
    with pytest.raises(IntegrityError, match="CHECK"):
        db.commit()


def test_naive_datetimes_are_refused(db: Session, learner: User) -> None:
    learner.hearts_updated_at = datetime(2026, 10, 8, 12, 0)  # no time zone
    with pytest.raises(StatementError, match="naive datetime"):
        db.commit()


# Content


def test_unknown_exercise_type_is_refused(db: Session, lesson: Lesson) -> None:
    lesson.exercises.append(Exercise(position=2, type="speak", prompt="Hola"))
    with pytest.raises(IntegrityError, match="CHECK"):
        db.commit()


def test_only_match_pairs_may_omit_the_prompt(db: Session, lesson: Lesson) -> None:
    lesson.exercises.append(Exercise(position=2, type=ExerciseType.MATCH_PAIRS))
    db.commit()

    lesson.exercises.append(Exercise(position=3, type=ExerciseType.MULTIPLE_CHOICE))
    with pytest.raises(IntegrityError, match="CHECK"):
        db.commit()


def test_an_exercise_has_at_most_one_correct_option(db: Session, lesson: Lesson) -> None:
    exercise = Exercise(position=2, type=ExerciseType.MULTIPLE_CHOICE, prompt="the coffee")
    exercise.options = [
        ExerciseOption(position=1, text="el café", is_correct=True),
        ExerciseOption(position=2, text="el té"),
        ExerciseOption(position=3, text="la leche"),
    ]
    lesson.exercises.append(exercise)
    db.commit()

    exercise.options[1].is_correct = True
    with pytest.raises(IntegrityError, match="UNIQUE"):
        db.commit()


def test_an_exercise_has_at_most_one_primary_answer(db: Session, lesson: Lesson) -> None:
    lesson.exercises[0].accepted_answers.append(AcceptedAnswer(text="One coffee, please.", is_primary=True))
    with pytest.raises(IntegrityError, match="UNIQUE"):
        db.commit()


def test_deleting_a_unit_deletes_everything_beneath_it(db: Session, lesson: Lesson) -> None:
    skill_id, exercise_id = lesson.skill_id, lesson.exercises[0].id
    db.execute(delete(Unit).where(Unit.id == lesson.skill.unit_id))
    db.commit()

    assert db.scalar(select(func.count()).select_from(Lesson).where(Lesson.skill_id == skill_id)) == 0
    assert (
        db.scalar(
            select(func.count()).select_from(AcceptedAnswer).where(AcceptedAnswer.exercise_id == exercise_id)
        )
        == 0
    )
    assert db.get(Exercise, exercise_id) is None


def test_content_with_answers_cannot_be_deleted(db: Session, lesson: Lesson, learner: User) -> None:
    session = finished_session(lesson, learner)
    session.answers.append(
        SessionAnswer(
            exercise=lesson.exercises[0], answer="A coffee please", is_correct=True, answered_at=NOW
        )
    )
    db.add(session)
    db.commit()

    with pytest.raises(IntegrityError, match="FOREIGN KEY"):  # RESTRICT refuses at once, not at commit
        db.execute(delete(Lesson).where(Lesson.id == lesson.id))


# Activity history


@pytest.mark.parametrize(
    ("status", "finished_at"),
    [(SessionStatus.COMPLETED, None), (SessionStatus.IN_PROGRESS, NOW)],
    ids=["finished-without-time", "in-progress-with-time"],
)
def test_session_finish_time_matches_its_status(
    db: Session, lesson: Lesson, learner: User, status: SessionStatus, finished_at: datetime | None
) -> None:
    session = finished_session(lesson, learner)
    session.status, session.finished_at = status, finished_at
    db.add(session)
    with pytest.raises(IntegrityError, match="CHECK"):
        db.commit()


@pytest.mark.parametrize(("amount", "source"), [(0, XpSource.LESSON), (10, "bribe")])
def test_xp_events_are_positive_and_from_a_known_source(
    db: Session, learner: User, amount: int, source: str
) -> None:
    db.add(XpEvent(user_id=learner.id, amount=amount, source=source, earned_at=NOW, local_date=NOW.date()))
    with pytest.raises(IntegrityError, match="CHECK"):
        db.commit()


def test_achievements_can_only_be_unlocked_at_existing_tiers(db: Session, learner: User) -> None:
    wildfire = db.scalars(select(Achievement).where(Achievement.key == "wildfire")).one()
    # The seed unlocked tier 1 (the demo learner has a 3 day streak).
    db.add(UserAchievement(user_id=learner.id, achievement_id=wildfire.id, tier=2, unlocked_at=NOW))
    db.commit()

    db.add(UserAchievement(user_id=learner.id, achievement_id=wildfire.id, tier=99, unlocked_at=NOW))
    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        db.commit()


def test_deleting_a_learner_deletes_everything_they_own(db: Session, lesson: Lesson, learner: User) -> None:
    session = finished_session(lesson, learner)
    session.answers.append(
        SessionAnswer(
            exercise=lesson.exercises[0], answer="A coffee please", is_correct=True, answered_at=NOW
        )
    )
    wildfire = db.scalars(select(Achievement).where(Achievement.key == "wildfire")).one()
    db.add_all(
        [
            session,
            UserSkillProgress(user_id=learner.id, skill_id=lesson.skill_id, lessons_completed=1),
            XpEvent(
                user_id=learner.id,
                session=session,
                amount=10,
                source=XpSource.LESSON,
                earned_at=NOW,
                local_date=NOW.date(),
            ),
            UserAchievement(user_id=learner.id, achievement_id=wildfire.id, tier=2, unlocked_at=NOW),
        ]
    )
    db.commit()

    exercises_before = count(db, Exercise)
    db.execute(delete(User).where(User.id == learner.id))
    db.commit()

    owned = [UserSettings, UserSkillProgress, LessonSession, SessionAnswer, XpEvent, UserAchievement]
    assert {model.__tablename__: count(db, model) for model in owned} == dict.fromkeys(
        (model.__tablename__ for model in owned), 0
    )
    assert count(db, Exercise) == exercises_before  # content is untouched
    assert db.scalar(select(func.count()).where(LeagueMembership.user_id == learner.id)) == 0


# Leagues


def test_a_learner_is_in_one_league_a_week(db: Session, learner: User) -> None:
    (week,) = db.scalars(select(LeagueMembership.week_start).where(LeagueMembership.user_id == learner.id))
    silver = db.scalars(select(League).where(League.name == "Silver")).one()
    db.add(LeagueMembership(user_id=learner.id, week_start=week, league=silver, joined_at=NOW))

    with pytest.raises(IntegrityError, match="UNIQUE"):
        db.commit()


@pytest.mark.parametrize(
    ("model", "column", "value"),
    [
        (Rival, "active_days", 8),
        (Rival, "daily_xp", 0),
        (LeagueMembership, "final_rank", 0),
        (League, "promotion_count", -1),
    ],
)
def test_league_values_stay_in_range(db: Session, model: type[Base], column: str, value: int) -> None:
    row = db.scalars(select(model)).first()
    setattr(row, column, value)

    with pytest.raises(IntegrityError, match="CHECK"):
        db.commit()


def test_a_league_with_members_cannot_be_deleted(db: Session) -> None:
    with pytest.raises(IntegrityError, match="FOREIGN KEY"):
        db.execute(delete(League).where(League.name == "Bronze"))
