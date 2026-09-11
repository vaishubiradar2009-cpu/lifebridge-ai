import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True

    with app.test_client() as client:
        yield client


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_health_check(client):
    response = client.get("/api/health")

    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "ok"


def test_analyze_rejects_empty_situation(client):
    response = client.post(
        "/api/analyze",
        json={
            "situation": ""
        }
    )

    assert response.status_code == 400

    data = response.get_json()
    assert data["success"] is False
