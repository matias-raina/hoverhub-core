from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models.application import Application, ApplicationUpdate


class IApplicationRepository(ABC):
    @abstractmethod
    def create(self, application: Application) -> Application:
        """Create a new application in the database."""

    @abstractmethod
    def get_by_id(self, application_id: UUID) -> Application | None:
        """Retrieve an application by ID."""

    @abstractmethod
    def list_by_job(self, job_id: UUID, offset: int = 0, limit: int = 100) -> list[Application]:
        """List applications for a given job."""

    @abstractmethod
    def list_by_account(
        self, account_id: UUID, offset: int = 0, limit: int = 100
    ) -> list[Application]:
        """List applications submitted by an account."""

    @abstractmethod
    def update(self, application_id: UUID, application: ApplicationUpdate) -> Application | None:
        """Update an application (e.g. change status or message)."""

    @abstractmethod
    def delete(self, application_id: UUID) -> bool:
        """Delete (or withdraw) an application by ID."""
