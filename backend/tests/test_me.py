from datetime import UTC, date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.main import create_app
from app.models import User
from tests.conftest import NOW, FixedClock


def test_me_is_the_seeded_default_learner(client: TestClient) -> None:
    body = client.get("/api/v1/me").json()

    assert body["username"] == "alex"
    assert body["display_name"] == "Alex"
    assert body["active_course"]["title"] == "Spanish"
    assert body["daily_goal_xp"] == 20
    assert body["gems"] == 500
    assert body["hearts"] == {"current": 5, "max": 5, "next_heart_at": None, "regen_minutes": 30}
    assert body["streak"] == {"length": 0, "extended_today": False, "longest": 0}


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
