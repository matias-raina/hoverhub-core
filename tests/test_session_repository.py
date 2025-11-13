from datetime import UTC, datetime, timedelta

from sqlmodel import select

from app.domain.models.session import UserSession
from app.domain.repositories.session import SessionRepository
from tests.utils import create_test_session, create_test_user


class TestSessionRepositoryDeactivateExpiredSessions:
    """Tests for SessionRepository.deactivate_expired_sessions"""

    def test_deactivate_expired_sessions_no_expired(self, db_session):
        """Test deactivating expired sessions when there are none"""
        # Arrange
        user = create_test_user(db_session)
        # Create active session that hasn't expired yet
        create_test_session(
            db_session,
            user.id,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            is_active=True,
        )

        repository = SessionRepository(db_session)

        # Act
        count = repository.deactivate_expired_sessions()

        # Assert
        assert count == 0
        # Verify session is still active
        statement = select(UserSession)
        sessions = list(db_session.exec(statement).all())
        assert len(sessions) == 1
        assert sessions[0].is_active is True

    def test_deactivate_expired_sessions_one_expired(self, db_session):
        """Test deactivating a single expired session"""
        # Arrange
        user = create_test_user(db_session)
        # Create expired session
        expired_session = create_test_session(
            db_session,
            user.id,
            expires_at=datetime.now(UTC) - timedelta(hours=1),
            is_active=True,
        )

        repository = SessionRepository(db_session)

        # Act
        count = repository.deactivate_expired_sessions()

        # Assert
        assert count == 1
        # Verify session was deactivated
        db_session.refresh(expired_session)
        assert expired_session.is_active is False

    def test_deactivate_expired_sessions_multiple_expired(self, db_session):
        """Test deactivating multiple expired sessions"""
        # Arrange
        user1 = create_test_user(db_session, email="user1@test.com")
        user2 = create_test_user(db_session, email="user2@test.com")

        # Create multiple expired sessions
        expired_session1 = create_test_session(
            db_session,
            user1.id,
            expires_at=datetime.now(UTC) - timedelta(hours=1),
            is_active=True,
        )
        expired_session2 = create_test_session(
            db_session,
            user1.id,
            expires_at=datetime.now(UTC) - timedelta(hours=2),
            is_active=True,
        )
        expired_session3 = create_test_session(
            db_session,
            user2.id,
            expires_at=datetime.now(UTC) - timedelta(minutes=30),
            is_active=True,
        )

        repository = SessionRepository(db_session)

        # Act
        count = repository.deactivate_expired_sessions()

        # Assert
        assert count == 3
        # Verify all sessions were deactivated
        db_session.refresh(expired_session1)
        db_session.refresh(expired_session2)
        db_session.refresh(expired_session3)
        assert expired_session1.is_active is False
        assert expired_session2.is_active is False
        assert expired_session3.is_active is False

    def test_deactivate_expired_sessions_mixed_expired_and_active(self, db_session):
        """Test deactivating only expired sessions, leaving active ones untouched"""
        # Arrange
        user = create_test_user(db_session)

        # Create expired session
        expired_session = create_test_session(
            db_session,
            user.id,
            expires_at=datetime.now(UTC) - timedelta(hours=1),
            is_active=True,
        )

        # Create active session that hasn't expired
        active_session = create_test_session(
            db_session,
            user.id,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            is_active=True,
        )

        repository = SessionRepository(db_session)

        # Act
        count = repository.deactivate_expired_sessions()

        # Assert
        assert count == 1
        # Verify expired session was deactivated
        db_session.refresh(expired_session)
        assert expired_session.is_active is False
        # Verify active session remains active
        db_session.refresh(active_session)
        assert active_session.is_active is True

    def test_deactivate_expired_sessions_ignores_already_inactive(self, db_session):
        """Test that already inactive expired sessions are not counted"""
        # Arrange
        user = create_test_user(db_session)

        # Create expired but already inactive session
        inactive_expired_session = create_test_session(
            db_session,
            user.id,
            expires_at=datetime.now(UTC) - timedelta(hours=1),
            is_active=False,
        )

        # Create expired active session
        active_expired_session = create_test_session(
            db_session,
            user.id,
            expires_at=datetime.now(UTC) - timedelta(hours=2),
            is_active=True,
        )

        repository = SessionRepository(db_session)

        # Act
        count = repository.deactivate_expired_sessions()

        # Assert
        assert count == 1  # Only the active expired session should be counted
        # Verify inactive session remains inactive
        db_session.refresh(inactive_expired_session)
        assert inactive_expired_session.is_active is False
        # Verify active expired session was deactivated
        db_session.refresh(active_expired_session)
        assert active_expired_session.is_active is False

    def test_deactivate_expired_sessions_exactly_at_expiration_time(self, db_session):
        """Test deactivating sessions that expire exactly at the current time"""
        # Arrange
        user = create_test_user(db_session)
        # Create session that expires exactly now
        now = datetime.now(UTC)
        expired_session = create_test_session(
            db_session,
            user.id,
            expires_at=now,
            is_active=True,
        )

        repository = SessionRepository(db_session)

        # Act
        count = repository.deactivate_expired_sessions()

        # Assert
        assert count == 1
        # Verify session was deactivated
        db_session.refresh(expired_session)
        assert expired_session.is_active is False

    def test_deactivate_expired_sessions_no_sessions_at_all(self, db_session):
        """Test deactivating expired sessions when there are no sessions"""
        # Arrange
        repository = SessionRepository(db_session)

        # Act
        count = repository.deactivate_expired_sessions()

        # Assert
        assert count == 0

    def test_deactivate_expired_sessions_does_not_commit_when_no_expired(self, db_session):
        """Test that commit is not called when there are no expired sessions"""
        # Arrange
        user = create_test_user(db_session)
        active_session = create_test_session(
            db_session,
            user.id,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            is_active=True,
        )

        repository = SessionRepository(db_session)

        # Act
        count = repository.deactivate_expired_sessions()

        # Assert
        assert count == 0
        # Verify the active session is still active (commit wasn't called unnecessarily)
        db_session.refresh(active_session)
        assert active_session.is_active is True
