from uuid import UUID

from fastapi import status

from tests.utils import create_test_session, create_test_user, get_auth_headers


class TestGetCurrentUser:
    """Tests for GET /users/me"""

    def test_get_current_user_success(self, client):
        """Test getting current user with valid token"""
        # Signup to get a token
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "me@example.com",
                "password": "password123",
            },
        )
        assert signup_response.status_code == status.HTTP_201_CREATED
        token = signup_response.json()["access_token"]
        user_data = signup_response.json()["user"]

        # Get current user
        response = client.get(
            "/users/me",
            headers=get_auth_headers(token),
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == user_data["id"]
        assert data["email"] == "me@example.com"
        assert data["is_active"] is True
        assert "created_at" in data

    def test_get_current_user_unauthenticated(self, client):
        """Test getting current user without token returns 403"""
        response = client.get("/users/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_invalid_token(self, client):
        """Test getting current user with invalid token returns 401"""
        response = client.get(
            "/users/me",
            headers=get_auth_headers("invalid_token"),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_expired_token(self, client):
        """Test getting current user with expired token returns 401"""
        # Signup to get a token
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "expired@example.com",
                "password": "password123",
            },
        )
        token = signup_response.json()["access_token"]

        # Signout to invalidate the token
        client.post(
            "/auth/signout",
            headers=get_auth_headers(token),
        )

        # Try to use the invalidated token
        response = client.get(
            "/users/me",
            headers=get_auth_headers(token),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUserSessions:
    """Tests for GET /users/sessions"""

    def test_get_user_sessions_success(self, client, db_session):
        """Test getting user sessions with valid token"""
        # Signup to get a token
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "sessions@example.com",
                "password": "password123",
            },
        )
        assert signup_response.status_code == status.HTTP_201_CREATED
        token = signup_response.json()["access_token"]
        user_id = signup_response.json()["user"]["id"]

        create_test_session(db_session, UUID(user_id), host="192.168.1.1")
        create_test_session(db_session, UUID(user_id), host="192.168.1.2")

        # Get user sessions
        response = client.get(
            "/users/sessions",
            headers=get_auth_headers(token),
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        # Should have at least 3 sessions (1 from signup + 2 created)
        assert len(data) >= 3

        # Verify session structure
        for session in data:
            assert "id" in session
            assert "user_id" in session
            assert "host" in session
            assert "is_active" in session
            assert "created_at" in session
            assert "updated_at" in session
            assert session["user_id"] == user_id

    def test_get_user_sessions_empty(self, client, db_session):
        """Test getting sessions for user with no sessions"""
        # Create a user manually (without signup, so no session)
        create_test_user(
            db_session,
            email="nosessions@example.com",
            password="password123",
        )

        # Signin to create a session and get token
        signin_response = client.post(
            "/auth/signin",
            json={
                "email": "nosessions@example.com",
                "password": "password123",
            },
        )
        token = signin_response.json()["access_token"]

        # Get user sessions - should have at least 1 (from signin)
        response = client.get(
            "/users/sessions",
            headers=get_auth_headers(token),
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the session from signin

    def test_get_user_sessions_unauthenticated(self, client):
        """Test getting user sessions without token returns 403"""
        response = client.get("/users/sessions")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_sessions_invalid_token(self, client):
        """Test getting user sessions with invalid token returns 401"""
        response = client.get(
            "/users/sessions",
            headers=get_auth_headers("invalid_token"),
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_sessions_only_active(self, client, db_session):
        """Test that only active sessions are returned"""
        # Signup to get a token
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "active@example.com",
                "password": "password123",
            },
        )
        token = signup_response.json()["access_token"]
        user_id = signup_response.json()["user"]["id"]

        inactive_session = create_test_session(
            db_session,
            UUID(user_id),
            host="192.168.1.100",
            is_active=False,
        )

        # Get user sessions
        response = client.get(
            "/users/sessions",
            headers=get_auth_headers(token),
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Check that inactive session is not in the list
        # (Note: The service filters by is_active=True, so inactive sessions shouldn't appear)
        session_ids = [s["id"] for s in data]
        assert str(inactive_session.id) not in session_ids
