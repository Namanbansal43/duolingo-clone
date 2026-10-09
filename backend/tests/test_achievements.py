"""Achievements and the profile's XP history: levels reached, progress towards the next, and announcements."""

from datetime import timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import User
from app.services.achievements import unlock_achievements
from tests.conftest import NOW, FixedClock
from tests.test_sessions import answer, exercise_of, finish, nodes, play_through, start, start_active


def achievements(client: TestClient) -> dict[str, dict]:
    response = client.get("/api/v1/me/achievements")
    assert response.status_code == 200
    return {achievement["key"]: achievement for achievement in response.json()}


def progress(achievement: dict) -> tuple[int, int, int, str]:
    return achievement["level"], achievement["value"], achievement["goal"], achievement["description"]


def play_lesson(client: TestClient, db: Session, played: dict) -> dict:
    play_through(client, db, played)
    return finish(client, played)


def test_the_demo_history_has_earned_first_levels(client: TestClient) -> None:
    earned = achievements(client)

    assert list(earned) == ["wildfire", "sage", "scholar", "sharpshooter"]  # display order
    # A 3 day streak, 30 XP, 3 lessons, all without a mistake.
    assert progress(earned["wildfire"]) == (1, 3, 7, "Reach a 7 day streak")
    assert progress(earned["sage"]) == (0, 30, 100, "Earn 100 XP")
    assert progress(earned["scholar"]) == (0, 3, 5, "Complete 5 lessons")
    assert progress(earned["sharpshooter"]) == (1, 3, 10, "Complete 10 lessons without a mistake")
    assert (earned["wildfire"]["max_level"], earned["sharpshooter"]["max_level"]) == (10, 4)
    assert earned["wildfire"]["unlocked_at"] == "2026-10-08T12:00:00Z"
    assert earned["sage"]["unlocked_at"] is None


def test_finishing_a_session_announces_new_levels_once(client: TestClient, db: Session) -> None:
    assert play_lesson(client, db, start_active(client))["achievements"] == []  # 4 lessons

    say_hello = nodes(client)[0]
    done = play_lesson(client, db, start(client, say_hello["id"]))  # practice counts: 5 lessons

    (scholar,) = done["achievements"]
    assert (scholar["key"], scholar["title"]) == ("scholar", "Scholar")
    assert progress(scholar) == (1, 5, 10, "Complete 10 lessons")
    assert progress(achievements(client)["scholar"]) == progress(scholar)
    assert play_lesson(client, db, start(client, say_hello["id"]))["achievements"] == []


def test_a_mistake_spoils_a_perfect_lesson(client: TestClient, db: Session) -> None:
    played = start_active(client)
    answer(client, played, exercise_of(played, "type_answer")["id"], text="No idea")
    play_lesson(client, db, played)

    earned = achievements(client)
    assert earned["scholar"]["value"] == 4
    assert earned["sharpshooter"]["value"] == 3


def test_levels_are_kept_after_a_streak_ends(client: TestClient, clock: FixedClock) -> None:
    clock.advance(timedelta(days=5))  # the streak lapses, the longest streak stays

    assert client.get("/api/v1/me").json()["streak"]["length"] == 0
    assert progress(achievements(client)["wildfire"]) == (1, 3, 7, "Reach a 7 day streak")


def test_the_last_level_keeps_its_goal(client: TestClient, db: Session, learner: User) -> None:
    learner.total_xp = 40_000

    (sage,) = unlock_achievements(db, learner, NOW)
    db.commit()

    assert (sage.level, sage.max_level, sage.goal, sage.description) == (10, 10, 30_000, "Earn 30000 XP")
    assert unlock_achievements(db, learner, NOW) == []  # already stored


def test_xp_history_counts_each_day(client: TestClient, db: Session) -> None:
    play_lesson(client, db, start_active(client))  # today, 2026-10-08

    response = client.get("/api/v1/me/xp-history")

    assert response.status_code == 200
    assert response.json() == [
        {"day": "2026-10-02", "xp": 0},
        {"day": "2026-10-03", "xp": 0},
        {"day": "2026-10-04", "xp": 0},
        {"day": "2026-10-05", "xp": 10},  # the demo history: one lesson on each of the 3 days before
        {"day": "2026-10-06", "xp": 10},
        {"day": "2026-10-07", "xp": 10},
        {"day": "2026-10-08", "xp": 10},
    ]
    assert len(client.get("/api/v1/me/xp-history", params={"days": 31}).json()) == 31


def test_xp_history_length_is_limited(client: TestClient) -> None:
    for days in (0, 32):
        response = client.get("/api/v1/me/xp-history", params={"days": days})
        assert (response.status_code, response.json()["error"]["code"]) == (422, "validation_error")
