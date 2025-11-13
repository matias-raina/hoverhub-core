from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.domain.models.application import Application
from app.dto.application import CreateApplicationDto, UpdateApplicationStatusDto


class IApplicationService(ABC):
    @abstractmethod
    def apply_to_job(self, user_id: UUID, job_id: UUID, dto: CreateApplicationDto) -> Application:
        """Create an application for a job by a droner account belonging to user."""

    @abstractmethod
    def list_applications_for_job(self, user_id: UUID, job_id: UUID) -> Sequence[Application]:
        """List applications for a job (only if user owns employer account of the job)."""

    @abstractmethod
    def list_applications_for_user(self, user_id: UUID) -> Sequence[Application]:
        """List all applications submitted by any droner account of the user."""

    @abstractmethod
    def update_application_status(
        self,
        user_id: UUID,
        application_id: UUID,
        dto: UpdateApplicationStatusDto,
    ) -> Application:
        """Update application status (withdraw by droner or accept/reject by employer)."""

    @abstractmethod
    def delete_application(self, user_id: UUID, application_id: UUID) -> bool:
        """Delete (hard remove) an application; only droner owner can perform."""
