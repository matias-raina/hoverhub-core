from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_register_user():
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["username"] == user_data["username"]


def test_login_user():
    login_data = {
        "username": "testuser",
        "password": "securepassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_user_invalid_credentials():
    login_data = {
        "username": "testuser",
        "password": "wrongpassword"
    }
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_register_user_existing_email():
    user_data = {
        "username": "anotheruser",
        "email": "testuser@example.com",  # Using existing email
        "password": "securepassword"
    }
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"
