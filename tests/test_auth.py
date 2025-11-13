from fastapi import status

from tests.utils import create_test_user


class TestSignup:
    """Tests for POST /auth/signup"""

    def test_signup_success(self, client):
        """Test successful user signup"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "securepass123",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "user" in data
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "newuser@example.com"
        assert "id" in data["user"]
        assert "created_at" in data["user"]

    def test_signup_duplicate_email(self, client, db_session):
        """Test signup with duplicate email returns 409"""
        # Create existing user
        create_test_user(db_session, email="existing@example.com")

        response = client.post(
            "/auth/signup",
            json={
                "email": "existing@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "already exists" in response.json()["detail"].lower()

    def test_signup_invalid_email(self, client):
        """Test signup with invalid email format"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "not-an-email",
                "password": "password123",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signup_short_password(self, client):
        """Test signup with password shorter than 8 characters"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "user@example.com",
                "password": "short",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSignin:
    """Tests for POST /auth/signin"""

    def test_signin_success(self, client, db_session):
        """Test successful signin"""
        # Create user first
        create_test_user(
            db_session,
            email="signin@example.com",
            password="testpassword123",
        )

        response = client.post(
            "/auth/signin",
            json={
                "email": "signin@example.com",
                "password": "testpassword123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_signin_wrong_password(self, client, db_session):
        """Test signin with wrong password returns 401"""
        create_test_user(
            db_session,
            email="user@example.com",
            password="correctpassword123",
        )

        response = client.post(
            "/auth/signin",
            json={
                "email": "user@example.com",
                "password": "wrongpassword123",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_signin_nonexistent_user(self, client):
        """Test signin with non-existent user returns 401"""
        response = client.post(
            "/auth/signin",
            json={
                "email": "nonexistent@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid" in response.json()["detail"].lower()

    def test_signin_invalid_email(self, client):
        """Test signin with invalid email format"""
        response = client.post(
            "/auth/signin",
            json={
                "email": "not-an-email",
                "password": "password123",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_signin_short_password(self, client):
        """Test signin with password shorter than 8 characters"""
        response = client.post(
            "/auth/signin",
            json={
                "email": "user@example.com",
                "password": "short",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestSignout:
    """Tests for POST /auth/signout"""

    def test_signout_success(self, client):
        """Test successful signout"""
        # Signup to get a token
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "signout@example.com",
                "password": "password123",
            },
        )
        assert signup_response.status_code == status.HTTP_201_CREATED
        token = signup_response.json()["access_token"]

        # Signout
        response = client.post(
            "/auth/signout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_signout_invalid_token(self, client):
        """Test signout with invalid token returns 401"""
        response = client.post(
            "/auth/signout",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_signout_missing_token(self, client):
        """Test signout without token returns 401"""
        response = client.post("/auth/signout")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_signout_after_signout(self, client):
        """Test that token is invalidated after signout"""
        # Signup and get token
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "signout2@example.com",
                "password": "password123",
            },
        )
        token = signup_response.json()["access_token"]

        # Signout
        signout_response = client.post(
            "/auth/signout",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert signout_response.status_code == status.HTTP_204_NO_CONTENT

        # Try to use the token again - should fail
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestRefresh:
    """Tests for POST /auth/refresh"""

    def test_refresh_success(self, client):
        """Test successful token refresh"""
        # Signup to get tokens
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "refresh@example.com",
                "password": "password123",
            },
        )
        refresh_token = signup_response.json()["refresh_token"]

        # Refresh token
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        # New tokens should be different
        assert data["access_token"] != signup_response.json()["access_token"]
        assert data["refresh_token"] != refresh_token

    def test_refresh_invalid_token(self, client):
        """Test refresh with invalid token returns 401"""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid_token"},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_access_token_fails(self, client):
        """Test that using access token as refresh token fails"""
        # Signup to get tokens
        signup_response = client.post(
            "/auth/signup",
            json={
                "email": "refresh2@example.com",
                "password": "password123",
            },
        )
        access_token = signup_response.json()["access_token"]

        # Try to use access token as refresh token
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": access_token},
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_missing_token(self, client):
        """Test refresh without token returns 422"""
        response = client.post("/auth/refresh", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
