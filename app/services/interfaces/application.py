from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.domain.models.application import Application
from app.dto.application import CreateApplicationDto


class IApplicationService(ABC):
    @abstractmethod
    def apply_to_job(
        self, account_id: UUID, job_id: UUID, dto: CreateApplicationDto
    ) -> Application:
        """Create an application for a job by a droner account belonging to user."""

    @abstractmethod
    def list_applications_for_job(self, account_id: UUID, job_id: UUID) -> Sequence[Application]:
        """List applications for a job (only if account owns the job)."""

    @abstractmethod
    def list_applications_for_account(self, account_id: UUID) -> Sequence[Application]:
        """List all applications submitted by the account."""

    @abstractmethod
    def get_application(self, account_id: UUID, application_id: UUID) -> Application:
        """Get a single application by ID. Accessible by DRONER owner or job owner."""

    @abstractmethod
    def withdraw_application(self, account_id: UUID, application_id: UUID) -> Application:
        """Withdraw an application (set status to WITHDRAWN); only droner owner can perform."""

    @abstractmethod
    def accept_application(self, account_id: UUID, application_id: UUID) -> Application:
        """Accept an application (set status to ACCEPTED); only job owner can perform."""

    @abstractmethod
    def reject_application(self, account_id: UUID, application_id: UUID) -> Application:
        """Reject an application (set status to REJECTED); only job owner can perform."""
