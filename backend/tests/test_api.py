from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.deps import get_current_user
from app.models import User
from app.seed import data
from tests.conftest import FixedClock


def test_health(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}


def test_courses_in_display_order_with_only_spanish_available(client: TestClient) -> None:
    courses = client.get("/api/v1/courses").json()

    assert len(courses) == len(data.COURSES)
    assert [c["learning_language"] for c in courses[:3]] == ["es", "fr", "de"]
    assert [c["title"] for c in courses if c["is_available"]] == ["Spanish"]


def test_courses_count_the_learners_studying_them(client: TestClient, db: Session, clock: FixedClock) -> None:
    spanish, french = client.get("/api/v1/courses").json()[:2]
    assert (spanish["learners"], french["learners"]) == (30, 0)  # the learner and the 29 seeded rivals

    db.add_all(
        User(
            username=f"student{i}",
            display_name=f"Student {i}",
            created_at=clock.now(),
            hearts_updated_at=clock.now(),
            active_course_id=spanish["id"],
        )
        for i in range(2)
    )
    db.commit()

    assert client.get("/api/v1/courses").json()[0]["learners"] == 32


def test_unknown_route_uses_the_error_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/nothing-here")

    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "message": "Not Found"}}


def test_unexpected_errors_use_the_error_envelope(app: FastAPI) -> None:
    def broken_user() -> None:
        raise RuntimeError("database on fire")

    app.dependency_overrides[get_current_user] = broken_user
    with TestClient(app, raise_server_exceptions=False) as client:
        response = client.get("/api/v1/me")

    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "internal_error", "message": "Something went wrong on our side."}
    }


def test_openapi_documents_the_real_error_shape(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    patch_me = spec["paths"]["/api/v1/me"]["patch"]["responses"]

    for status in ("404", "409", "422", "503"):
        assert patch_me[status]["content"]["application/json"]["schema"] == {
            "$ref": "#/components/schemas/ErrorOut"
        }
    assert "HTTPValidationError" not in spec["components"]["schemas"]  # FastAPI's default shape isn't ours
