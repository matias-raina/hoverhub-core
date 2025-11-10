from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from app.domain.models.application import Application, ApplicationUpdate
from app.domain.repositories.interfaces.application import IApplicationRepository


class ApplicationRepository(IApplicationRepository):
    def __init__(self, session: Session):
        self.session = session

    def create(self, application: Application) -> Application:
        """Create a new application entry in the database."""
        self.session.add(application)
        self.session.commit()
        self.session.refresh(application)
        return application

    def get_by_id(self, application_id: UUID) -> Optional[Application]:
        """Retrieve an application by ID."""
        return self.session.get(Application, application_id)

    def list_by_job(
        self, job_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[Application]:
        """List applications for a given job."""
        statement = (
            select(Application)
            .where(Application.job_id == job_id)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def list_by_account(
        self, account_id: UUID, offset: int = 0, limit: int = 100
    ) -> List[Application]:
        """List applications submitted by an account."""
        statement = (
            select(Application)
            .where(Application.account_id == account_id)
            .offset(offset)
            .limit(limit)
        )
        return self.session.exec(statement).all()

    def update(
        self, application_id: UUID, application: ApplicationUpdate
    ) -> Optional[Application]:
        """Update an existing application entry."""
        db_app = self.get_by_id(application_id)
        if not db_app:
            return None
        app_data = application.model_dump(exclude_unset=True)
        # SQLModel provides sqlmodel_update to apply dict updates
        db_app.sqlmodel_update(app_data)
        self.session.add(db_app)
        self.session.commit()
        self.session.refresh(db_app)
        return db_app

    def delete(self, application_id: UUID) -> bool:
        """Delete (withdraw) an application by ID."""
        db_app = self.get_by_id(application_id)
        if db_app:
            self.session.delete(db_app)
            self.session.commit()
            return True
        return False
