from abc import ABC, abstractmethod
from collections.abc import Sequence
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
    def get_by_job_id(self, job_id: UUID, offset: int, limit: int) -> Sequence[Application]:
        """List applications for a given job."""

    @abstractmethod
    def get_by_account_id(self, account_id: UUID, offset: int, limit: int) -> Sequence[Application]:
        """List applications submitted by an account."""

    @abstractmethod
    def update(self, application_id: UUID, application: ApplicationUpdate) -> Application | None:
        """Update an existing application entry."""

    @abstractmethod
    def delete(self, application_id: UUID) -> bool:
        """Delete an application by ID."""
