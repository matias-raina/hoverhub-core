import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


@pytest.fixture
def application_data():
    return {
        "job_id": 1,
        "user_id": 1,
        "status": "pending"
    }


def test_submit_application(application_data):
    response = client.post("/applications/", json=application_data)
    assert response.status_code == 201
    assert response.json()["job_id"] == application_data["job_id"]
    assert response.json()["user_id"] == application_data["user_id"]
    assert response.json()["status"] == application_data["status"]


def test_get_applications():
    response = client.get("/applications/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_application_by_id():
    response = client.get("/applications/1")
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert "user_id" in response.json()
    assert "status" in response.json()


def test_update_application(application_data):
    application_data["status"] = "accepted"
    response = client.put("/applications/1", json=application_data)
    assert response.status_code == 200
    assert response.json()["status"] == application_data["status"]


def test_delete_application():
    response = client.delete("/applications/1")
    assert response.status_code == 204
    response = client.get("/applications/1")
    assert response.status_code == 404
