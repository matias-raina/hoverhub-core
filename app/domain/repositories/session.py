from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, desc, select

from app.domain.models.session import UserSession
from app.domain.repositories.interfaces.session import ISessionRepository


class SessionRepository(ISessionRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, session: UserSession) -> UserSession:
        """Create a new session in the database."""
        self.session.add(session)
        self.session.commit()
        self.session.refresh(session)
        return session

    def get_by_id(self, session_id: UUID) -> Optional[UserSession]:
        """Get a session by its ID."""
        return self.session.get(UserSession, session_id)

    def deactivate(self, session_id: UUID) -> Optional[UserSession]:
        """Deactivate an existing session."""
        session = self.session.get(UserSession, session_id)
        if session:
            session.is_active = False
            self.session.add(session)
            self.session.commit()
            self.session.refresh(session)
        return session

    def update(self, session: UserSession) -> UserSession:
        """Update an existing session."""
        self.session.add(session)
        self.session.commit()
        self.session.refresh(session)
        return session

    def get_all_by_user_id(self, user_id: UUID) -> List[UserSession]:
        """Retrieve all sessions by user ID."""
        statement = (
            select(UserSession)
            .where(UserSession.user_id == user_id)
            .where(UserSession.is_active)
            .order_by(desc(UserSession.created_at))
        )
        return list(self.session.exec(statement).all())

    def deactivate_expired_sessions(self) -> int:
        """Deactivate all expired sessions and return the count of deactivated sessions."""
        now = datetime.now(timezone.utc)
        statement = (
            select(UserSession)
            .where(UserSession.is_active)
            .where(UserSession.expires_at <= now)
        )
        expired_sessions = list(self.session.exec(statement).all())

        for session in expired_sessions:
            session.is_active = False
            self.session.add(session)

        if expired_sessions:
            self.session.commit()

        return len(expired_sessions)
