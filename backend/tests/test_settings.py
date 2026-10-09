"""The settings page: the learner's preferences, and the demo tools that move time and start over."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.rules import LESSON_XP
from tests.test_path import get_path
from tests.test_sessions import finish, play_through, start_active

DEFAULTS = {
    "sound_effects": True,
    "animations": True,
    "motivational_messages": True,
    "listening_exercises": True,
    "dark_mode": "system",
}


def test_preferences_start_at_duolingos_defaults(client: TestClient) -> None:
    assert client.get("/api/v1/me/settings").json() == DEFAULTS


def test_changing_some_preferences_keeps_the_rest(client: TestClient) -> None:
    changed = client.patch("/api/v1/me/settings", json={"sound_effects": False, "dark_mode": "on"})

    assert changed.status_code == 200
    expected = DEFAULTS | {"sound_effects": False, "dark_mode": "on"}
    assert changed.json() == expected
    assert client.get("/api/v1/me/settings").json() == expected


@pytest.mark.parametrize("body", [{"dark_mode": "dim"}, {"dark_mode": True}, {"volume": 3}])
def test_invalid_preferences_are_refused(client: TestClient, body: dict) -> None:
    response = client.patch("/api/v1/me/settings", json=body)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"
    assert client.get("/api/v1/me/settings").json() == DEFAULTS


def test_starting_over_keeps_preferences(client: TestClient) -> None:
    client.patch("/api/v1/me/settings", json={"animations": False})
    course_id = client.get("/api/v1/me").json()["active_course"]["id"]
    choices = {"active_course_id": course_id, "daily_goal_xp": 10, "timezone": "UTC"}

    assert client.post("/api/v1/me/onboarding", json=choices).status_code == 200
    assert client.get("/api/v1/me/settings").json()["animations"] is False


# Demo tools


def test_advancing_a_day_moves_the_apps_clock(client: TestClient) -> None:
    assert client.get("/api/v1/demo/clock").json() == {"days_ahead": 0, "now": "2026-10-08T12:00:00Z"}
    assert client.get("/api/v1/me").json()["streak"]["length"] == 3  # the last lesson was yesterday

    advanced = client.post("/api/v1/demo/clock/advance").json()

    assert advanced == {"days_ahead": 1, "now": "2026-10-09T12:00:00Z"}
    me = client.get("/api/v1/me").json()
    assert me["now"] == "2026-10-09T12:00:00Z"
    assert me["streak"]["length"] == 0  # a whole day went by without a lesson


def test_lessons_after_advancing_count_on_the_new_day(client: TestClient, db: Session) -> None:
    client.post("/api/v1/demo/clock/advance")

    played = start_active(client)
    play_through(client, db, played)
    finish(client, played)

    history = client.get("/api/v1/me/xp-history?days=2").json()
    assert [day["day"] for day in history] == ["2026-10-08", "2026-10-09"]
    assert history[0]["xp"] == 0
    assert history[1]["xp"] >= LESSON_XP
    assert client.get("/api/v1/me").json()["streak"]["length"] == 1  # a new streak starts


def test_advancing_past_sunday_ends_the_league_week(client: TestClient) -> None:
    assert client.get("/api/v1/leaderboard").json()["last_result"] is None

    for _ in range(4):  # Thursday to Monday
        client.post("/api/v1/demo/clock/advance")

    board = client.get("/api/v1/leaderboard").json()
    assert board["week_start"] == "2026-10-12"
    assert board["last_result"]["week_start"] == "2026-10-05"


def test_emptying_hearts(client: TestClient) -> None:
    hearts = client.post("/api/v1/demo/hearts/empty").json()["hearts"]

    assert hearts == {"current": 0, "max": 5, "next_heart_at": "2026-10-08T12:30:00Z", "regen_minutes": 30}
    response = client.post("/api/v1/sessions", json={"skill_id": get_path(client)["active_node_id"]})
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "out_of_hearts"


def test_resetting_the_demo_restores_the_seeded_learner(client: TestClient, db: Session) -> None:
    client.patch("/api/v1/me/settings", json={"dark_mode": "on"})
    played = start_active(client)
    play_through(client, db, played)
    finish(client, played)
    client.post("/api/v1/demo/clock/advance")
    client.post("/api/v1/demo/hearts/empty")
    course_id = client.get("/api/v1/me").json()["active_course"]["id"]
    choices = {"active_course_id": course_id, "daily_goal_xp": 10, "timezone": "UTC"}
    client.post("/api/v1/me/onboarding", json=choices)

    me = client.post("/api/v1/demo/reset").json()

    assert me["is_guest"] is False
    assert (me["total_xp"], me["lessons_completed"], me["now"]) == (30, 3, "2026-10-08T12:00:00Z")
    assert me["streak"] == {"length": 3, "extended_today": False, "longest": 3}
    assert me["hearts"]["current"] == 5
    assert client.get("/api/v1/demo/clock").json()["days_ahead"] == 0
    assert client.get("/api/v1/me/settings").json()["dark_mode"] == "on"  # preferences are kept
    board = client.get("/api/v1/leaderboard").json()
    assert (board["league"]["name"], len(board["standings"])) == ("Bronze", 30)
