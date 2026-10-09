"""The guest from "Get started" and signing in: two learners, kept apart by the `learner` cookie."""

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from tests.test_achievements import play_lesson
from tests.test_leaderboard import board
from tests.test_me import get_started
from tests.test_sessions import nodes, start, start_active


def me(client: TestClient) -> dict:
    return client.get("/api/v1/me").json()


def become_guest(client: TestClient) -> dict:
    response = client.post("/api/v1/me/onboarding", json=get_started(client))
    assert response.status_code == 200
    return response.json()


def test_get_started_sets_the_guest_cookie(client: TestClient) -> None:
    response = client.post("/api/v1/me/onboarding", json=get_started(client))

    cookie = response.headers["set-cookie"]
    assert cookie.startswith("learner=guest;")
    assert "HttpOnly" in cookie and "SameSite=lax" in cookie
    assert me(client)["username"] == "guest"


def test_a_browser_without_the_cookie_is_still_the_demo_learner(client: TestClient) -> None:
    become_guest(client)

    client.cookies.clear()  # another browser, or "I already have an account" in a fresh window
    demo = me(client)

    assert (demo["username"], demo["is_guest"], demo["lessons_completed"]) == ("alex", False, 3)
    assert demo["streak"]["length"] == 3


def test_getting_started_again_starts_the_guest_over(client: TestClient, db: Session) -> None:
    first = become_guest(client)
    play_lesson(client, db, start_active(client))
    assert me(client)["lessons_completed"] == 1

    again = become_guest(client)

    assert again["id"] == first["id"]  # the same guest, from the start
    assert (again["lessons_completed"], again["total_xp"]) == (0, 0)
    assert len(db.scalars(select(User).where(User.username == "guest")).all()) == 1


def test_signing_in_returns_to_the_demo_learner(client: TestClient, db: Session) -> None:
    become_guest(client)
    play_lesson(client, db, start_active(client))  # the guest's progress
    client.patch("/api/v1/me/settings", json={"dark_mode": "on"})

    response = client.post("/api/v1/me/sign-in")

    assert response.status_code == 200
    demo = response.json()
    assert (demo["username"], demo["is_guest"], demo["lessons_completed"]) == ("alex", False, 3)
    assert 'learner=""' in response.headers["set-cookie"]  # cleared
    assert me(client) == demo
    assert client.get("/api/v1/me/settings").json()["dark_mode"] == "on"  # preferences carry over
    assert board(client)["joined"] is True  # the demo learner's league is still there

    # Progress made after signing in stays with the demo learner.
    play_lesson(client, db, start_active(client))
    assert me(client)["lessons_completed"] == 4


def test_signing_in_as_the_demo_learner_changes_nothing(client: TestClient) -> None:
    before = me(client)

    response = client.post("/api/v1/me/sign-in")

    assert response.status_code == 200
    assert response.json() == before


def test_a_guest_must_sign_in_to_join_the_leaderboard(client: TestClient, db: Session) -> None:
    become_guest(client)
    locked = board(client)
    assert (locked["unlocked"], locked["lessons_to_unlock"], locked["sign_in_required"]) == (False, 10, False)

    first_node = nodes(client)[0]["id"]  # its two lessons, then practice
    unlocked = [play_lesson(client, db, start(client, first_node))["leaderboard_unlocked"] for _ in range(10)]

    assert unlocked == [False] * 10  # a guest never joins a league
    league = board(client)
    assert (league["unlocked"], league["lessons_to_unlock"], league["sign_in_required"]) == (False, 0, True)
    assert (league["league"], league["joined"], league["standings"]) == (None, False, [])
    assert all(row["user_id"] != me(client)["id"] for row in board(TestClient(client.app))["standings"])


def test_resetting_the_demo_removes_the_guest(client: TestClient, db: Session) -> None:
    become_guest(client)

    response = client.post("/api/v1/demo/reset")

    assert response.json()["username"] == "alex"
    assert 'learner=""' in response.headers["set-cookie"]
    assert db.scalar(select(User).where(User.username == "guest")) is None
    assert me(client)["username"] == "alex"


def test_a_stale_guest_cookie_falls_back_to_the_demo_learner(client: TestClient) -> None:
    become_guest(client)
    client.post("/api/v1/demo/reset")
    client.cookies.set("learner", "guest")  # a browser that missed the reset

    assert me(client)["username"] == "alex"


def test_two_browsers_keep_their_own_learner(client: TestClient) -> None:
    other = TestClient(client.app)  # a second browser on the same server
    become_guest(other)

    assert me(other)["username"] == "guest"
    assert me(client)["username"] == "alex"
    assert me(client)["lessons_completed"] == 3
