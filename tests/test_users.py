import pytest
from src.models.user import User
from src.repositories.user_repository import UserRepository
from src.services.user_service import UserService

@pytest.fixture
def user_service():
    return UserService(UserRepository())

@pytest.fixture
def sample_user():
    return User(id=1, username="testuser", email="test@example.com", password="hashed_password")

def test_create_user(user_service, sample_user):
    user = user_service.create_user(sample_user)
    assert user.username == sample_user.username
    assert user.email == sample_user.email

def test_get_user_by_id(user_service, sample_user):
    user_service.create_user(sample_user)
    user = user_service.get_user_by_id(sample_user.id)
    assert user.id == sample_user.id
    assert user.username == sample_user.username

def test_update_user(user_service, sample_user):
    user_service.create_user(sample_user)
    sample_user.username = "updateduser"
    updated_user = user_service.update_user(sample_user)
    assert updated_user.username == "updateduser"

def test_delete_user(user_service, sample_user):
    user_service.create_user(sample_user)
    user_service.delete_user(sample_user.id)
    user = user_service.get_user_by_id(sample_user.id)
    assert user is None

def test_user_creation_with_invalid_email(user_service):
    with pytest.raises(ValueError):
        user_service.create_user(User(id=2, username="invaliduser", email="invalid_email", password="hashed_password"))