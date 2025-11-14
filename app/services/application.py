from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status

from app.domain.models.account import Account, AccountType
from app.domain.models.application import Application, ApplicationStatus, ApplicationUpdate
from app.domain.repositories.interfaces.account import IAccountRepository
from app.domain.repositories.interfaces.application import IApplicationRepository
from app.domain.repositories.interfaces.job import IJobRepository
from app.dto.application import CreateApplicationDto
from app.services.interfaces.application import IApplicationService


class ApplicationService(IApplicationService):
    def __init__(
        self,
        application_repository: IApplicationRepository,
        account_repository: IAccountRepository,
        job_repository: IJobRepository,
    ):
        self.application_repository = application_repository
        self.account_repository = account_repository
        self.job_repository = job_repository

    def _get_employer_accounts(self, user_id: UUID) -> Sequence[Account]:
        return self.account_repository.get_user_accounts(user_id, AccountType.EMPLOYER)

    def apply_to_job(
        self, account_id: UUID, job_id: UUID, dto: CreateApplicationDto
    ) -> Application:
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        account = self.account_repository.get_by_id(account_id)

        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        if account.account_type != AccountType.DRONER:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is not a droner account",
            )

        # Check if application already exists
        existing_application = self.application_repository.get_by_job_and_account(
            job.id, account.id
        )
        if existing_application:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application already exists for this account and job",
            )

        application = Application(job_id=job.id, account_id=account.id, message=dto.message)
        return self.application_repository.create(application)

    def list_applications_for_job(self, account_id: UUID, job_id: UUID) -> Sequence[Application]:
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        if account.account_type != AccountType.EMPLOYER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view applications for this job",
            )

        if job.account_id != account.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this job",
            )

        return self.application_repository.get_by_job_id(job.id, offset=0, limit=1000)

    def list_applications_for_account(self, account_id: UUID) -> Sequence[Application]:
        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
        if account.account_type != AccountType.DRONER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this resource",
            )
        return self.application_repository.get_by_account_id(account.id, offset=0, limit=1000)

    def get_application(self, account_id: UUID, application_id: UUID) -> Application:
        """Get a single application by ID. Accessible by DRONER owner or job owner."""
        application = self.application_repository.get_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )

        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

        # Check if account is the DRONER owner of the application
        if account.account_type == AccountType.DRONER and application.account_id == account.id:
            return application

        # Check if account is the EMPLOYER owner of the job
        if account.account_type == AccountType.EMPLOYER:
            job = self.job_repository.get_by_id(application.job_id)
            if job and job.account_id == account.id:
                return application

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this application",
        )

    def withdraw_application(self, account_id: UUID, application_id: UUID) -> Application:
        """Withdraw an application (set status to WITHDRAWN); only droner owner can perform."""
        application = self.application_repository.get_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )

        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

        if account.account_type != AccountType.DRONER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only droner accounts can withdraw applications",
            )

        if application.account_id != account.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to withdraw this application",
            )

        application_update = ApplicationUpdate(status=ApplicationStatus.WITHDRAWN)
        updated = self.application_repository.update(application_id, application_update)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update application",
            )
        return updated

    def accept_application(self, account_id: UUID, application_id: UUID) -> Application:
        """Accept an application (set status to ACCEPTED); only job owner can perform."""
        application = self.application_repository.get_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )

        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

        if account.account_type != AccountType.EMPLOYER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only employer accounts can accept applications",
            )

        job = self.job_repository.get_by_id(application.job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        if job.account_id != account.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to accept applications for this job",
            )

        application_update = ApplicationUpdate(status=ApplicationStatus.ACCEPTED)
        updated = self.application_repository.update(application_id, application_update)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update application",
            )
        return updated

    def reject_application(self, account_id: UUID, application_id: UUID) -> Application:
        """Reject an application (set status to REJECTED); only job owner can perform."""
        application = self.application_repository.get_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )

        account = self.account_repository.get_by_id(account_id)
        if not account:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

        if account.account_type != AccountType.EMPLOYER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only employer accounts can reject applications",
            )

        job = self.job_repository.get_by_id(application.job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        if job.account_id != account.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to reject applications for this job",
            )

        application_update = ApplicationUpdate(status=ApplicationStatus.REJECTED)
        updated = self.application_repository.update(application_id, application_update)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update application",
            )
        return updated
