from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.main import create_app
from app.models import LessonSession, User, UserAchievement, UserSkillProgress, XpEvent
from app.services.rules import STARTING_GEMS
from tests.conftest import NOW, FixedClock


def test_me_is_the_seeded_default_learner(client: TestClient) -> None:
    body = client.get("/api/v1/me").json()

    assert body["username"] == "alex"
    assert body["display_name"] == "Alex"
    assert body["active_course"]["title"] == "Spanish"
    assert body["daily_goal_xp"] == 20
    assert body["gems"] == 500
    assert body["hearts"] == {"current": 5, "max": 5, "next_heart_at": None, "regen_minutes": 30}
    # Seeded history (data.DEMO_HISTORY): 3 lessons of 10 XP on the three days before today.
    assert (body["total_xp"], body["lessons_completed"], body["xp_today"]) == (30, 3, 0)
    assert body["streak"] == {"length": 3, "extended_today": False, "longest": 3}


def test_hearts_regenerate_while_away(client: TestClient, db: Session, learner: User) -> None:
    learner.hearts = 2
    learner.hearts_updated_at = NOW - timedelta(minutes=65)  # 10:55
    db.commit()

    hearts = client.get("/api/v1/me").json()["hearts"]

    assert hearts["current"] == 4  # two full 30-minute intervals have passed
    assert hearts["next_heart_at"] == "2026-10-08T12:25:00Z"  # the third interval ends at 12:25


@pytest.mark.parametrize(
    ("last_day", "length", "extended_today"),
    [
        (NOW.date(), 6, True),
        (NOW.date() - timedelta(days=1), 6, False),
        (NOW.date() - timedelta(days=2), 0, False),
    ],
    ids=["active-today", "active-yesterday", "missed-a-day"],
)
def test_streak_lapses_after_a_missed_day(
    client: TestClient, db: Session, learner: User, last_day: date, length: int, extended_today: bool
) -> None:
    learner.current_streak = learner.longest_streak = 6
    learner.last_streak_date = last_day
    db.commit()

    streak = client.get("/api/v1/me").json()["streak"]

    assert streak == {"length": length, "extended_today": extended_today, "longest": 6}


def test_streak_day_follows_the_learner_time_zone(
    client: TestClient, db: Session, learner: User, clock: FixedClock
) -> None:
    clock.current = datetime(2026, 10, 9, 2, 0, tzinfo=UTC)  # still the evening of Oct 8 in New York
    learner.timezone = "America/New_York"
    learner.current_streak = learner.longest_streak = 3
    learner.last_streak_date = date(2026, 10, 8)
    db.commit()

    assert client.get("/api/v1/me").json()["streak"]["extended_today"] is True


def test_update_daily_goal_and_time_zone(client: TestClient) -> None:
    response = client.patch("/api/v1/me", json={"daily_goal_xp": 30, "timezone": "Asia/Kolkata"})

    assert response.status_code == 200
    assert response.json()["daily_goal_xp"] == 30
    saved = client.get("/api/v1/me").json()
    assert (saved["daily_goal_xp"], saved["timezone"]) == (30, "Asia/Kolkata")


@pytest.mark.parametrize(
    "payload",
    [{"daily_goal_xp": 25}, {"timezone": "Mars/Olympus_Mons"}, {"gems": 99999}],
    ids=["goal-not-an-option", "unknown-time-zone", "field-not-editable"],
)
def test_update_rejects_invalid_input(client: TestClient, payload: dict) -> None:
    response = client.patch("/api/v1/me", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_cannot_switch_to_a_coming_soon_course(client: TestClient) -> None:
    french = next(c for c in client.get("/api/v1/courses").json() if c["learning_language"] == "fr")

    response = client.patch("/api/v1/me", json={"active_course_id": french["id"]})

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "course_unavailable"
    assert client.get("/api/v1/me").json()["active_course"]["title"] == "Spanish"


def test_unknown_course_is_not_found(client: TestClient) -> None:
    response = client.patch("/api/v1/me", json={"active_course_id": 9999})

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "course_not_found"


def test_me_reports_a_missing_learner(settings: Settings, clock: FixedClock) -> None:
    unseeded = settings.model_copy(update={"seed_on_startup": False})
    with TestClient(create_app(unseeded, clock=clock)) as client:
        response = client.get("/api/v1/me")

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "learner_missing"


@pytest.mark.parametrize("payload", [{}, {"daily_goal_xp": None, "timezone": None}], ids=["empty", "nulls"])
def test_omitted_or_null_fields_are_left_unchanged(client: TestClient, payload: dict) -> None:
    before = client.get("/api/v1/me").json()

    response = client.patch("/api/v1/me", json=payload)

    assert response.status_code == 200
    assert response.json() == before


def get_started(client: TestClient, **overrides: object) -> dict:
    """The choices the "Get started" flow sends at the end, for the learner's current course."""
    spanish_id = client.get("/api/v1/me").json()["active_course"]["id"]
    return {"active_course_id": spanish_id, "daily_goal_xp": 30, "timezone": "Asia/Kolkata"} | overrides


def test_get_started_begins_a_new_learner(client: TestClient, db: Session, learner: User) -> None:
    # On top of the seeded history and achievements: spent hearts and gems, and a streak freeze.
    learner.hearts, learner.gems, learner.streak_freezes = 2, 120, 1
    db.commit()
    assert db.scalar(select(func.count()).select_from(UserAchievement)) > 0

    response = client.post("/api/v1/me/onboarding", json=get_started(client))

    assert response.status_code == 200
    me = response.json()
    assert me["active_course"]["title"] == "Spanish"
    assert (me["daily_goal_xp"], me["timezone"]) == (30, "Asia/Kolkata")
    assert me["joined_at"] == "2026-10-08T12:00:00Z"
    assert (me["total_xp"], me["xp_today"], me["lessons_completed"], me["gems"]) == (0, 0, 0, STARTING_GEMS)
    assert me["hearts"] == {"current": 5, "max": 5, "next_heart_at": None, "regen_minutes": 30}
    assert me["streak"] == {"length": 0, "extended_today": False, "longest": 0}
    assert client.get("/api/v1/me").json() == me
    assert {a["level"] for a in client.get("/api/v1/me/achievements").json()} == {0}

    path = client.get(f"/api/v1/courses/{me['active_course']['id']}/path").json()
    nodes = [node for unit in path["units"] for node in unit["nodes"]]
    assert [node["state"] for node in nodes] == ["active"] + ["locked"] * (len(nodes) - 1)
    assert all(node["lessons_completed"] == 0 for node in nodes)
    assert path["active_node_id"] == nodes[0]["id"]

    for model in (LessonSession, XpEvent, UserSkillProgress, UserAchievement):
        assert db.scalar(select(func.count()).select_from(model).where(model.user_id == learner.id)) == 0
    assert db.get(User, learner.id).streak_freezes == 0


@pytest.mark.parametrize(
    "change",
    [
        {"daily_goal_xp": None},
        {"daily_goal_xp": 25},
        {"timezone": "Mars/Olympus_Mons"},
        {"gems": 99999},
    ],
    ids=["missing-goal", "goal-not-an-option", "unknown-time-zone", "unknown-field"],
)
def test_get_started_rejects_invalid_choices(client: TestClient, change: dict) -> None:
    choices = {key: value for key, value in (get_started(client) | change).items() if value is not None}
    before = client.get("/api/v1/me").json()

    response = client.post("/api/v1/me/onboarding", json=choices)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert client.get("/api/v1/me").json() == before


@pytest.mark.parametrize(
    ("course", "status", "code"),
    [("fr", 409, "course_unavailable"), (None, 404, "course_not_found")],
    ids=["coming-soon", "unknown"],
)
def test_get_started_keeps_the_history_when_the_course_is_refused(
    client: TestClient, course: str | None, status: int, code: str
) -> None:
    courses = {c["learning_language"]: c["id"] for c in client.get("/api/v1/courses").json()}
    before = client.get("/api/v1/me").json()

    response = client.post(
        "/api/v1/me/onboarding", json=get_started(client, active_course_id=courses.get(course, 9999))
    )

    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert client.get("/api/v1/me").json() == before  # still 30 XP, 3 lessons, a 3-day streak
