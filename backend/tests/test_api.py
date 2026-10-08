from fastapi.testclient import TestClient

from app.seed import data


def test_health(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}


def test_courses_in_display_order_with_only_spanish_available(client: TestClient) -> None:
    courses = client.get("/api/v1/courses").json()

    assert len(courses) == len(data.COURSES)
    assert [c["learning_language"] for c in courses[:3]] == ["es", "fr", "de"]
    assert [c["title"] for c in courses if c["is_available"]] == ["Spanish"]


def test_unknown_route_uses_the_error_envelope(client: TestClient) -> None:
    response = client.get("/api/v1/nothing-here")

    assert response.status_code == 404
    assert response.json() == {"error": {"code": "not_found", "message": "Not Found"}}
