from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_add_favorite():
    favorite_data = {"job_id": 1, "user_id": 1}
    response = client.post("/favorites", json=favorite_data)
    assert response.status_code == 201
    assert response.json() == {"job_id": 1, "user_id": 1}


def test_get_favorites():
    response = client.get("/favorites?user_id=1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_add_favorite_invalid_job():
    favorite_data = {"job_id": 999, "user_id": 1}
    response = client.post("/favorites", json=favorite_data)
    assert response.status_code == 404  # Assuming job_id 999 does not exist


def test_get_favorites_no_user():
    response = client.get("/favorites?user_id=999")
    assert response.status_code == 404  # Assuming user_id 999 does not exist


def test_remove_favorite():
    favorite_data = {"job_id": 1, "user_id": 1}
    response = client.delete("/favorites", json=favorite_data)
    assert response.status_code == 204  # Assuming successful deletion


def test_remove_favorite_not_found():
    favorite_data = {"job_id": 999, "user_id": 1}
    response = client.delete("/favorites", json=favorite_data)
    assert response.status_code == 404  # Assuming favorite does not exist
