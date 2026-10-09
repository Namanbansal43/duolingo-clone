"""Playing lessons through the API: starting, answering, finishing, quitting, and hearts along the way."""

from datetime import timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Exercise, ExerciseType, LessonSession, SessionStatus, User
from app.services.rules import HEART_REFILL_GEMS, LESSON_XP, PRACTICE_XP
from tests.conftest import NOW, FixedClock
from tests.test_path import complete, get_path


def nodes(client: TestClient) -> list[dict]:
    return [node for unit in get_path(client)["units"] for node in unit["nodes"]]


def start(client: TestClient, skill_id: int) -> dict:
    response = client.post("/api/v1/sessions", json={"skill_id": skill_id})
    assert response.status_code == 201, response.json()
    return response.json()


def start_active(client: TestClient) -> dict:
    return start(client, get_path(client)["active_node_id"])


def answer(client: TestClient, session: dict, exercise_id: int, **body: object) -> dict:
    response = client.post(
        f"/api/v1/sessions/{session['id']}/answers", json={"exercise_id": exercise_id, **body}
    )
    assert response.status_code == 200, response.json()
    return response.json()


def right_answers(db: Session, played: dict) -> list[tuple[int, list[dict]]]:
    """For every exercise of a played session, the request bodies that answer it correctly."""
    by_id = {e["id"]: e for e in played["exercises"]}
    result = []
    for exercise in db.scalars(select(Exercise).where(Exercise.id.in_(by_id))):
        shown = by_id[exercise.id]
        tiles = {option["text"]: option["id"] for option in shown["options"]}
        primary = next((a.text for a in exercise.accepted_answers if a.is_primary), None)
        match exercise.type:
            case ExerciseType.MULTIPLE_CHOICE | ExerciseType.FILL_BLANK:
                bodies = [{"option_ids": [next(o.id for o in exercise.options if o.is_correct)]}]
            case ExerciseType.WORD_BANK | ExerciseType.LISTEN:
                words = [w.strip("¿¡?!.,") for w in primary.split()]
                bodies = [{"option_ids": [tiles[w] for w in words]}]
            case ExerciseType.TYPE_ANSWER:
                bodies = [{"text": primary}]
            case _:
                bodies = [{"pair": [o.match_text, o.text]} for o in exercise.options]
        result.append((exercise.id, bodies))
    return result


def play_through(client: TestClient, db: Session, played: dict, *, skip: set[str] = frozenset()) -> None:
    types = {e["id"]: e["type"] for e in played["exercises"]}
    for exercise_id, bodies in right_answers(db, played):
        if types[exercise_id] in skip:
            continue
        for body in bodies:
            answer(client, played, exercise_id, **body)


def finish(client: TestClient, played: dict) -> dict:
    response = client.post(f"/api/v1/sessions/{played['id']}/complete")
    assert response.status_code == 200, response.json()
    return response.json()


def exercise_of(played: dict, kind: str) -> dict:
    return next(e for e in played["exercises"] if e["type"] == kind)


def test_the_active_node_plays_its_next_lesson(client: TestClient) -> None:
    played = start_active(client)  # "Introduce yourself": lesson 1 of 2 is done

    assert (played["mode"], played["status"]) == ("lesson", "in_progress")
    assert (played["node"]["title"], played["lesson_position"], played["lessons_total"]) == (
        "Introduce yourself",
        2,
        2,
    )
    assert sorted(e["type"] for e in played["exercises"]) == sorted(
        ["multiple_choice", "word_bank", "match_pairs", "fill_blank", "type_answer", "listen"]
    )
    assert played["completed_exercise_ids"] == []
    assert exercise_of(played, "word_bank")["instruction"] == "Write this in Spanish"
    pairs = exercise_of(played, "match_pairs")["pairs"]
    assert len(pairs["left"]) == len(pairs["right"]) == 4
    # Nothing in the payload gives the answers away, and a reload shows the same order.
    assert "is_correct" not in str(played) and "accepted" not in str(played)
    assert client.get(f"/api/v1/sessions/{played['id']}").json() == played
    assert client.get("/api/v1/sessions/current").json() == played


def test_completed_nodes_are_practiced(client: TestClient) -> None:
    say_hello = nodes(client)[0]
    assert start(client, say_hello["id"])["mode"] == "practice"


def test_nodes_that_cannot_be_played(client: TestClient, db: Session, learner: User) -> None:
    path_nodes = nodes(client)
    chest, locked = path_nodes[2], path_nodes[3]
    for skill_id, status, code in [
        (chest["id"], 409, "not_a_lesson"),
        (locked["id"], 409, "skill_locked"),
        (9999, 404, "skill_not_found"),
    ]:
        response = client.post("/api/v1/sessions", json={"skill_id": skill_id})
        assert (response.status_code, response.json()["error"]["code"]) == (status, code)

    # With Unit 1 done, Unit 2's first node is next, but its lessons have no exercises yet.
    complete(db, learner, *(node["id"] for node in path_nodes[:5]))
    response = client.post("/api/v1/sessions", json={"skill_id": path_nodes[5]["id"]})
    assert (response.status_code, response.json()["error"]["code"]) == (409, "lesson_unavailable")


def test_a_wrong_answer_costs_a_heart(client: TestClient) -> None:
    played = start_active(client)
    choice = exercise_of(played, "multiple_choice")
    wrong = choice["options"][0]["id"]

    result = answer(client, played, choice["id"], option_ids=[wrong])
    if result["correct"]:  # the first option happened to be right; pick another
        played = start_active(client)
        choice = exercise_of(played, "multiple_choice")
        result = answer(client, played, choice["id"], option_ids=[choice["options"][1]["id"]])

    assert (result["correct"], result["verdict"]) == (False, "wrong")
    assert result["solution"] == "nice to meet you"
    assert result["hearts"]["current"] == 4
    assert result["hearts"]["next_heart_at"] == "2026-10-08T12:30:00Z"
    assert client.get("/api/v1/me").json()["hearts"]["current"] == 4


def test_skipping_counts_as_a_wrong_answer(client: TestClient) -> None:
    played = start_active(client)
    blank = exercise_of(played, "fill_blank")

    result = answer(client, played, blank["id"], skipped=True)

    assert (result["correct"], result["solution"], result["hearts"]["current"]) == (False, "Me llamo Ana.", 4)


def test_practice_never_costs_hearts(client: TestClient) -> None:
    played = start(client, nodes(client)[0]["id"])
    typed = exercise_of(played, "type_answer")

    result = answer(client, played, typed["id"], text="something else")

    assert (result["correct"], result["hearts"]["current"]) == (False, 5)


def test_typed_answers_forgive_a_typo(client: TestClient) -> None:
    played = start_active(client)
    typed = exercise_of(played, "type_answer")  # "Nice to meet you." -> "Mucho gusto."

    result = answer(client, played, typed["id"], text="mucho gsto")

    assert (result["correct"], result["verdict"], result["solution"]) == (True, "typo", "Mucho gusto.")
    assert result["exercise_completed"] is True


def test_match_pairs_are_checked_pair_by_pair(client: TestClient, db: Session) -> None:
    played = start_active(client)
    match_id, bodies = next(
        (eid, bodies) for eid, bodies in right_answers(db, played) if len(bodies) > 1
    )  # the match_pairs exercise: one body per pair

    left, other_right = bodies[0]["pair"][0], bodies[1]["pair"][1]
    wrong = answer(client, played, match_id, pair=[left, other_right])
    assert (wrong["correct"], wrong["exercise_completed"], wrong["hearts"]["current"]) == (False, False, 4)

    results = [answer(client, played, match_id, **body) for body in bodies]
    assert [r["exercise_completed"] for r in results] == [False, False, False, True]
    assert match_id in client.get(f"/api/v1/sessions/{played['id']}").json()["completed_exercise_ids"]


@pytest.mark.parametrize(
    "body",
    [{"text": "hola"}, {"option_ids": []}, {"option_ids": [999999]}, {"pair": ["a", "b"]}],
    ids=["text-for-a-choice", "no-option", "unknown-option", "pair-for-a-choice"],
)
def test_answers_of_the_wrong_shape_are_refused(client: TestClient, body: dict) -> None:
    played = start_active(client)
    choice = exercise_of(played, "multiple_choice")

    response = client.post(
        f"/api/v1/sessions/{played['id']}/answers", json={"exercise_id": choice["id"], **body}
    )

    assert (response.status_code, response.json()["error"]["code"]) == (422, "invalid_answer")


def test_finishing_a_lesson(client: TestClient, db: Session, clock: FixedClock) -> None:
    played = start_active(client)
    clock.advance(timedelta(minutes=2, seconds=5))
    play_through(client, db, played)

    done = finish(client, played)

    assert (done["xp_earned"], done["total_xp"], done["xp_today"], done["daily_goal_xp"]) == (
        LESSON_XP,
        40,
        10,
        20,
    )
    assert (done["accuracy"], done["duration_seconds"]) == (100, 125)
    assert done["streak"] == {"length": 4, "longest": 4, "extended": True}
    assert done["node"] == {
        "id": played["node"]["id"],
        "lessons_completed": 2,
        "lessons_total": 2,
        "completed": True,
    }
    # The node is done, so the chest after it is next; the streak now counts today.
    assert get_path(client)["active_node_id"] == nodes(client)[2]["id"]
    assert client.get("/api/v1/me").json()["streak"] == {"length": 4, "extended_today": True, "longest": 4}

    # A second session the same day earns XP but doesn't extend the streak again.
    practice = start(client, played["node"]["id"])
    play_through(client, db, practice)
    again = finish(client, practice)
    assert (again["xp_earned"], again["xp_today"], again["streak"]["extended"]) == (PRACTICE_XP, 15, False)


def test_accuracy_counts_first_tries(client: TestClient, db: Session) -> None:
    played = start_active(client)
    typed = exercise_of(played, "type_answer")
    answer(client, played, typed["id"], text="no idea")  # wrong first, then right below
    play_through(client, db, played)

    assert finish(client, played)["accuracy"] == 83  # 5 of 6


def test_unanswered_exercises_block_finishing_except_listening(client: TestClient, db: Session) -> None:
    played = start_active(client)
    play_through(client, db, played, skip={"listen", "fill_blank"})
    response = client.post(f"/api/v1/sessions/{played['id']}/complete")
    assert (response.status_code, response.json()["error"]["code"]) == (409, "session_incomplete")

    blank_id, bodies = next(
        (eid, b) for eid, b in right_answers(db, played) if eid == exercise_of(played, "fill_blank")["id"]
    )
    answer(client, played, blank_id, **bodies[0])
    assert finish(client, played)["node"]["completed"] is True  # "Can't listen now" skipped the listening


def test_running_out_of_hearts(client: TestClient, db: Session, learner: User) -> None:
    learner.hearts, learner.hearts_updated_at = 1, NOW
    db.commit()
    played = start_active(client)
    typed = exercise_of(played, "type_answer")

    assert answer(client, played, typed["id"], text="wrong")["hearts"]["current"] == 0
    response = client.post(
        f"/api/v1/sessions/{played['id']}/answers", json={"exercise_id": typed["id"], "text": "x"}
    )
    assert (response.status_code, response.json()["error"]["code"]) == (409, "out_of_hearts")
    response = client.post("/api/v1/sessions", json={"skill_id": played["node"]["id"]})
    assert (response.status_code, response.json()["error"]["code"]) == (409, "out_of_hearts")

    assert client.post(f"/api/v1/sessions/{played['id']}/quit").status_code == 204
    db.expire_all()
    assert db.get(LessonSession, played["id"]).status == SessionStatus.FAILED

    # Refilling costs gems; a full set can't be refilled again.
    refilled = client.post("/api/v1/me/hearts/refill")
    assert refilled.status_code == 200
    assert (refilled.json()["hearts"]["current"], refilled.json()["gems"]) == (5, 500 - HEART_REFILL_GEMS)
    response = client.post("/api/v1/me/hearts/refill")
    assert (response.status_code, response.json()["error"]["code"]) == (409, "hearts_full")


def test_a_refill_needs_enough_gems(client: TestClient, db: Session, learner: User) -> None:
    learner.hearts, learner.gems = 2, HEART_REFILL_GEMS - 1
    db.commit()

    response = client.post("/api/v1/me/hearts/refill")

    assert (response.status_code, response.json()["error"]["code"]) == (409, "not_enough_gems")


def test_practice_earns_a_heart_back(client: TestClient, db: Session, learner: User) -> None:
    learner.hearts, learner.hearts_updated_at = 2, NOW
    db.commit()
    practice = start(client, nodes(client)[0]["id"])
    play_through(client, db, practice)

    assert finish(client, practice)["hearts"]["current"] == 3


def test_ended_and_unknown_sessions(client: TestClient, db: Session) -> None:
    first = start_active(client)
    second = start_active(client)  # starting again abandons the unfinished one
    db.expire_all()
    assert db.get(LessonSession, first["id"]).status == SessionStatus.ABANDONED

    response = client.post(f"/api/v1/sessions/{first['id']}/complete")
    assert (response.status_code, response.json()["error"]["code"]) == (409, "session_finished")
    assert client.post(f"/api/v1/sessions/{second['id']}/quit").status_code == 204
    response = client.get("/api/v1/sessions/999999")
    assert (response.status_code, response.json()["error"]["code"]) == (404, "session_not_found")
    response = client.get("/api/v1/sessions/current")  # nothing in progress any more
    assert (response.status_code, response.json()["error"]["code"]) == (404, "session_not_found")
