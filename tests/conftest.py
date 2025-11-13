import tempfile
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine

from app.config.cache import get_cache
from app.config.database import get_db
from app.config.settings import Environment, Settings, get_settings
from app.main import app

# Create a temporary database file
with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as _test_db_file:
    _test_db_path = _test_db_file.name

TEST_DATABASE_URL = f"sqlite:///{_test_db_path}"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    Create a test database session.
    Creates all tables before test, drops them after.
    """
    # Create all tables on the engine
    SQLModel.metadata.create_all(test_engine)

    # Create session
    with Session(test_engine) as session:
        yield session

    # Clean up: drop all tables and delete data
    SQLModel.metadata.drop_all(test_engine)
    # Recreate tables for next test
    SQLModel.metadata.create_all(test_engine)


@pytest.fixture(scope="function")
def override_get_db(db_session: Session):
    """
    Override get_db dependency to use test database.

    Note: The parameter name 'db_session' must match the fixture name for pytest
    dependency injection to work. This is intentional pytest behavior, not a bug.
    """

    def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture(scope="function")
def mock_cache():
    """
    Mock Redis cache for testing.
    """
    mock_redis = MagicMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    mock_redis.exists.return_value = False

    app.dependency_overrides[get_cache] = lambda: mock_redis
    yield mock_redis
    app.dependency_overrides.pop(get_cache, None)


@pytest.fixture(scope="function")
def test_settings():
    """
    Override settings for testing.
    """
    test_settings = Settings(
        app_name="HoverHub Test",
        environment=Environment.DEVELOPMENT,
        host="0.0.0.0",
        port=8000,
        db_connection_string=TEST_DATABASE_URL,
        cache_connection_string="redis://localhost:6379/0",
        secret_key="test-secret-key-for-testing-only-not-for-production",
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_minutes=1440,
    )

    # Clear the cache to allow new settings
    get_settings.cache_clear()
    app.dependency_overrides[get_settings] = lambda: test_settings
    yield test_settings
    app.dependency_overrides.pop(get_settings, None)
    get_settings.cache_clear()


@pytest.fixture(scope="function")
def client(
    override_get_db,  # pytest fixture dependency (sets up db override)
    mock_cache,  # pytest fixture dependency (sets up cache mock)
    test_settings,  # pytest fixture dependency (sets up test settings)
) -> TestClient:
    """
    Create a test client with all dependencies overridden.

    Note: The fixture parameters are pytest dependencies that modify app.dependency_overrides.
    They must be listed here so pytest invokes them before creating the TestClient.
    """
    return TestClient(app)
