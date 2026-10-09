"""Hearts, streak and grading rules on their own, without a database."""

from datetime import UTC, date, datetime, timedelta

import pytest

from app.services.grading import Verdict, grade_text, normalize
from app.services.hearts import HeartsStatus, change_hearts, hearts_status
from app.services.streak import StreakStatus, StreakUpdate, extend_streak, local_date, streak_status

REGEN = timedelta(minutes=30)
T0 = datetime(2026, 10, 8, 12, 0, tzinfo=UTC)
TODAY = date(2026, 10, 8)


def hearts_after(stored: int, minutes: int) -> HeartsStatus:
    return hearts_status(
        stored=stored, max_hearts=5, updated_at=T0, now=T0 + timedelta(minutes=minutes), regen_every=REGEN
    )


def test_full_hearts_have_no_timer() -> None:
    assert hearts_after(5, 0) == HeartsStatus(current=5, max=5, next_heart_at=None)


def test_no_heart_before_a_full_interval() -> None:
    assert hearts_after(1, 29) == HeartsStatus(current=1, max=5, next_heart_at=T0 + REGEN)


def test_one_heart_per_interval() -> None:
    assert hearts_after(1, 60) == HeartsStatus(current=3, max=5, next_heart_at=T0 + 3 * REGEN)


def test_hearts_never_exceed_the_maximum() -> None:
    assert hearts_after(0, 10_000) == HeartsStatus(current=5, max=5, next_heart_at=None)


def test_clock_behind_the_anchor_regenerates_nothing() -> None:
    assert hearts_after(2, -15).current == 2


def test_no_streak_before_any_activity() -> None:
    assert streak_status(current=0, longest=0, last_date=None, today=TODAY) == StreakStatus(0, False, 0)


@pytest.mark.parametrize(
    ("days_ago", "expected"),
    [(0, StreakStatus(4, True, 9)), (1, StreakStatus(4, False, 9)), (2, StreakStatus(0, False, 9))],
)
def test_streak_survives_one_quiet_day_only(days_ago: int, expected: StreakStatus) -> None:
    last = TODAY - timedelta(days=days_ago)
    assert streak_status(current=4, longest=9, last_date=last, today=TODAY) == expected


def test_local_date_uses_the_learner_time_zone() -> None:
    evening_utc = datetime(2026, 10, 8, 20, 0, tzinfo=UTC)
    assert local_date(evening_utc, "UTC") == date(2026, 10, 8)
    assert local_date(evening_utc, "Asia/Kolkata") == date(2026, 10, 9)  # 01:30 the next day


def test_spending_a_full_heart_starts_the_regeneration_clock() -> None:
    later = T0 + timedelta(minutes=90)
    assert change_hearts(stored=5, max_hearts=5, updated_at=T0, now=later, regen_every=REGEN, delta=-1) == (
        4,
        later,
    )


def test_spending_keeps_regenerated_hearts_and_the_time_towards_the_next() -> None:
    # 2 stored at 12:00; by 13:05 two came back (4), and 5 minutes count towards the next one.
    now = T0 + timedelta(minutes=65)
    stored, anchor = change_hearts(
        stored=2, max_hearts=5, updated_at=T0, now=now, regen_every=REGEN, delta=-1
    )
    assert (stored, anchor) == (3, T0 + timedelta(minutes=60))
    assert hearts_status(
        stored=stored, max_hearts=5, updated_at=anchor, now=now, regen_every=REGEN
    ).next_heart_at == (T0 + timedelta(minutes=90))


def test_hearts_stay_between_zero_and_the_maximum() -> None:
    assert change_hearts(stored=0, max_hearts=5, updated_at=T0, now=T0, regen_every=REGEN, delta=-1)[0] == 0
    assert change_hearts(stored=5, max_hearts=5, updated_at=T0, now=T0, regen_every=REGEN, delta=2)[0] == 5


@pytest.mark.parametrize(
    ("last_date", "expected"),
    [
        (None, StreakUpdate(current=1, longest=9, last_date=TODAY, extended=True)),
        (TODAY - timedelta(days=1), StreakUpdate(current=5, longest=9, last_date=TODAY, extended=True)),
        (TODAY - timedelta(days=3), StreakUpdate(current=1, longest=9, last_date=TODAY, extended=True)),
        (TODAY, StreakUpdate(current=4, longest=9, last_date=TODAY, extended=False)),
    ],
    ids=["first-ever", "after-yesterday", "after-a-gap", "again-today"],
)
def test_finishing_a_lesson_extends_the_streak_once_a_day(
    last_date: date | None, expected: StreakUpdate
) -> None:
    assert extend_streak(current=4, longest=9, last_date=last_date, today=TODAY) == expected


def test_a_new_record_streak_becomes_the_longest() -> None:
    assert extend_streak(current=9, longest=9, last_date=TODAY - timedelta(days=1), today=TODAY).longest == 10


def test_normalizing_ignores_case_punctuation_and_spacing() -> None:
    assert normalize("  ¿Cómo  te LLAMAS? ") == "cómo te llamas"
    assert normalize("I\u2019m Ana.") == "i'm ana"


ACCEPTED = ["Goodbye.", "Bye.", "Good bye."]


@pytest.mark.parametrize(
    ("answer", "lenient", "verdict", "solution"),
    [
        ("goodbye", False, Verdict.CORRECT, None),
        ("Bye!", False, Verdict.OTHER_SOLUTION, "Goodbye."),
        ("Godbye", True, Verdict.TYPO, "Goodbye."),
        ("Godbye", False, Verdict.WRONG, "Goodbye."),
        ("Hello", True, Verdict.WRONG, "Goodbye."),
        ("by", True, Verdict.WRONG, "Goodbye."),  # too short for a typo to count
    ],
    ids=["exact", "other-solution", "typo", "typo-in-tiles", "wrong", "short-word"],
)
def test_grading_written_answers(answer: str, lenient: bool, verdict: Verdict, solution: str | None) -> None:
    grade = grade_text(answer, ACCEPTED, "Goodbye.", lenient=lenient)
    assert (grade.verdict, grade.solution) == (verdict, solution)


def test_a_missing_accent_is_a_typo() -> None:
    grade = grade_text("Adios", ["Adiós."], "Adiós.", lenient=True)
    assert (grade.verdict, grade.solution, grade.correct) == (Verdict.TYPO, "Adiós.", True)
