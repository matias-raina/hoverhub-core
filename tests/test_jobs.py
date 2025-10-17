from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_create_job():
    response = client.post(
        "/jobs", json={"title": "Test Job", "description": "Job description", "user_id": 1})
    assert response.status_code == 201
    assert response.json()["title"] == "Test Job"


def test_get_job():
    response = client.get("/jobs/1")
    assert response.status_code == 200
    assert "title" in response.json()


def test_update_job():
    response = client.put(
        "/jobs/1", json={"title": "Updated Job", "description": "Updated description"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Job"


def test_delete_job():
    response = client.delete("/jobs/1")
    assert response.status_code == 204
    assert response.content == b""  # No content expected on successful delete


def test_get_jobs():
    response = client.get("/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Expecting a list of jobs
