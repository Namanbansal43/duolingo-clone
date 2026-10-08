from datetime import timedelta

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import delete, func, select, text
from sqlalchemy.orm import Session

from app.core.config import BACKEND_DIR, Settings
from app.core.db import create_db_engine, run_migrations
from app.models import Lesson, LessonSession, Skill, Unit, User, UserSkillProgress, XpEvent, XpSource
from app.seed import data, seed_database, spanish
from app.services.rules import CHEST_GEMS
from tests.conftest import NOW, FixedClock


def get_path(client: TestClient) -> dict:
    spanish_id = client.get("/api/v1/me").json()["active_course"]["id"]
    response = client.get(f"/api/v1/courses/{spanish_id}/path")
    assert response.status_code == 200
    return response.json()


def node_states(path: dict) -> list[list[str]]:
    return [[node["state"] for node in unit["nodes"]] for unit in path["units"]]


def complete(db: Session, learner: User, *skill_ids: int) -> None:
    for skill_id in skill_ids:
        progress = db.get(UserSkillProgress, (learner.id, skill_id)) or UserSkillProgress(
            user_id=learner.id, skill_id=skill_id, lessons_completed=0
        )
        progress.completed_at = NOW
        db.add(progress)
    db.commit()


def test_seeded_learner_is_partway_through_unit_one(client: TestClient) -> None:
    path = get_path(client)

    assert [unit["title"] for unit in path["units"]] == [unit.title for unit in spanish.UNITS]
    unit_one = path["units"][0]["nodes"]
    assert [node["kind"] for node in unit_one] == ["lesson", "lesson", "chest", "lesson", "review"]
    assert [(node["lessons_completed"], node["lessons_total"]) for node in unit_one] == [
        (3, 3),
        (1, 3),
        (0, 0),
        (0, 3),
        (0, 2),
    ]
    assert node_states(path) == [
        ["completed", "active", "locked", "locked", "locked"],
        ["locked"] * 5,
        ["locked"] * 5,
    ]
    assert path["active_node_id"] == unit_one[1]["id"]


def test_a_new_learner_starts_at_the_first_node(client: TestClient, db: Session) -> None:
    db.execute(delete(UserSkillProgress))
    db.commit()

    states = node_states(get_path(client))

    assert states[0][0] == "active"
    assert all(state == "locked" for unit in states for state in unit if state != "active")


def test_finishing_a_unit_unlocks_the_next_one(client: TestClient, db: Session, learner: User) -> None:
    unit_one = get_path(client)["units"][0]["nodes"]
    complete(db, learner, *(node["id"] for node in unit_one))

    states = node_states(get_path(client))

    assert states[0] == ["completed"] * 5
    assert states[1][0] == "active"


def test_a_finished_course_has_no_active_node(client: TestClient, db: Session, learner: User) -> None:
    complete(db, learner, *db.scalars(select(Skill.id)))

    path = get_path(client)

    assert path["active_node_id"] is None
    assert all(state == "completed" for unit in node_states(path) for state in unit)


@pytest.mark.parametrize(
    ("course_id", "status", "code"), [(9999, 404, "course_not_found"), (2, 409, "course_unavailable")]
)
def test_path_needs_an_available_course(client: TestClient, course_id: int, status: int, code: str) -> None:
    response = client.get(f"/api/v1/courses/{course_id}/path")

    assert response.status_code == status
    assert response.json()["error"]["code"] == code


def test_opening_the_chest_once_it_is_reached(client: TestClient, db: Session, learner: User) -> None:
    unit_one = get_path(client)["units"][0]["nodes"]
    chest_id = unit_one[2]["id"]

    locked = client.post(f"/api/v1/skills/{chest_id}/open-chest")
    assert (locked.status_code, locked.json()["error"]["code"]) == (409, "skill_locked")

    complete(db, learner, unit_one[1]["id"])
    opened = client.post(f"/api/v1/skills/{chest_id}/open-chest")
    assert opened.status_code == 200
    assert opened.json() == {"gems_awarded": CHEST_GEMS, "gems": data.DEFAULT_LEARNER_GEMS + CHEST_GEMS}
    assert node_states(get_path(client))[0] == ["completed", "completed", "completed", "active", "locked"]

    again = client.post(f"/api/v1/skills/{chest_id}/open-chest")
    assert (again.status_code, again.json()["error"]["code"]) == (409, "chest_already_opened")


@pytest.mark.parametrize(
    ("node_index", "status", "code"), [(0, 409, "not_a_chest"), (None, 404, "skill_not_found")]
)
def test_only_chests_can_be_opened(
    client: TestClient, node_index: int | None, status: int, code: str
) -> None:
    skill_id = 9999 if node_index is None else get_path(client)["units"][0]["nodes"][node_index]["id"]

    response = client.post(f"/api/v1/skills/{skill_id}/open-chest")

    assert (response.status_code, response.json()["error"]["code"]) == (status, code)


def test_xp_today_counts_only_today_in_the_learner_time_zone(
    client: TestClient, db: Session, learner: User, clock: FixedClock
) -> None:
    learner.timezone = "Asia/Kolkata"  # NOW (12:00 UTC) is 17:30 on Oct 8 there
    db.add_all(
        [
            XpEvent(
                user_id=learner.id, amount=15, source=XpSource.LESSON, earned_at=NOW, local_date=NOW.date()
            ),
            XpEvent(
                user_id=learner.id,
                amount=10,
                source=XpSource.LESSON,
                earned_at=NOW - timedelta(days=1),
                local_date=NOW.date() - timedelta(days=1),
            ),
        ]
    )
    db.commit()

    assert client.get("/api/v1/me").json()["xp_today"] == 15


def test_seeded_content_and_history_are_consistent(
    db: Session, learner: User, settings: Settings, clock: FixedClock
) -> None:
    seed_database(db, default_username=settings.default_username, now=clock.now() + timedelta(days=5))

    def count(model: type) -> int:
        return db.scalar(select(func.count()).select_from(model))

    assert count(Unit) == len(spanish.UNITS)
    assert count(Skill) == sum(len(unit.skills) for unit in spanish.UNITS)
    assert count(Lesson) == sum(skill.lessons for unit in spanish.UNITS for skill in unit.skills)
    # Reseeding never adds a second history; the history matches the learner's totals.
    lessons_done = sum(lessons for _, lessons in data.DEMO_HISTORY)
    assert count(LessonSession) == lessons_done
    assert (
        db.scalar(select(func.sum(XpEvent.amount)).where(XpEvent.user_id == learner.id)) == learner.total_xp
    )


def test_downgrading_turns_review_nodes_into_lessons(settings: Settings) -> None:
    engine = create_db_engine(settings.database_url)
    run_migrations(engine)
    with engine.begin() as connection:
        connection.execute(
            text(
                "INSERT INTO courses (id, learning_language, from_language, title, position, is_available) "
                "VALUES (1, 'es', 'en', 'Spanish', 0, 1)"
            )
        )
        connection.execute(
            text("INSERT INTO units (id, course_id, position, title) VALUES (1, 1, 1, 'Unit')")
        )
        connection.execute(
            text(
                "INSERT INTO skills (id, unit_id, position, title, kind) "
                "VALUES (1, 1, 1, 'Unit review', 'review')"
            )
        )

    config = Config(str(BACKEND_DIR / "alembic.ini"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "0002")

    with engine.connect() as connection:
        kind = connection.execute(text("SELECT kind FROM skills WHERE id = 1")).scalar()
    engine.dispose()
    assert kind == "lesson"
