from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status

from app.domain.models.account import Account, AccountType
from app.domain.models.application import Application, ApplicationStatus, ApplicationUpdate
from app.domain.repositories.interfaces.account import IAccountRepository
from app.domain.repositories.interfaces.application import IApplicationRepository
from app.domain.repositories.interfaces.job import IJobRepository
from app.dto.application import CreateApplicationDto, UpdateApplicationStatusDto
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

    def _get_droner_accounts(self, user_id: UUID) -> Sequence[Account]:
        return self.account_repository.get_user_accounts(user_id, AccountType.DRONER)

    def _get_employer_accounts(self, user_id: UUID) -> Sequence[Account]:
        return self.account_repository.get_user_accounts(user_id, AccountType.EMPLOYER)

    def apply_to_job(self, user_id: UUID, job_id: UUID, dto: CreateApplicationDto) -> Application:
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

        droner_accounts = self._get_droner_accounts(user_id)
        if not droner_accounts:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User has no droner account to apply",
            )

        # Select first droner account for MVP
        applicant_account = droner_accounts[0]

        # Prevent duplicate application for same account & job
        existing = self.application_repository.get_by_job_id(job.id)
        if any(app.account_id == applicant_account.id for app in existing):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application already exists for this account and job",
            )

        application = Application(
            job_id=job.id,
            account_id=applicant_account.id,
            message=dto.message,
        )
        return self.application_repository.create(application)

    def list_applications_for_job(self, user_id: UUID, job_id: UUID) -> Sequence[Application]:
        job = self.job_repository.get_by_id(job_id)
        if not job:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
        employer_accounts = self._get_employer_accounts(user_id)
        employer_account_ids = {a.id for a in employer_accounts}
        if job.account_id not in employer_account_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view applications for this job",
            )
        return self.application_repository.get_by_job_id(job.id)

    def list_applications_for_user(self, user_id: UUID) -> Sequence[Application]:
        droner_accounts = self._get_droner_accounts(user_id)
        if not droner_accounts:
            return []
        apps: Sequence[Application] = []
        for acc in droner_accounts:
            apps.extend(self.application_repository.get_by_account_id(acc.id))
        return apps

    def update_application_status(
        self, user_id: UUID, application_id: UUID, dto: UpdateApplicationStatusDto
    ) -> Application:
        application = self.application_repository.get_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )

        droner_accounts = self._get_droner_accounts(user_id)
        employer_accounts = self._get_employer_accounts(user_id)
        droner_ids = {a.id for a in droner_accounts}
        employer_ids = {a.id for a in employer_accounts}

        # Withdraw logic
        if dto.status == ApplicationStatus.WITHDRAWN:
            if application.account_id not in droner_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not allowed to withdraw this application",
                )
        else:
            # Accept/Reject only by employer owning the job
            job = self.job_repository.get_by_id(application.job_id)
            if not job:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
            if job.account_id not in employer_ids:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not allowed to change status for this application",
                )

        application_update = ApplicationUpdate(status=dto.status, message=dto.message)
        updated = self.application_repository.update(application_id, application_update)
        if not updated:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )
        return updated

    def delete_application(self, user_id: UUID, application_id: UUID) -> bool:
        application = self.application_repository.get_by_id(application_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
            )
        droner_accounts = self._get_droner_accounts(user_id)
        droner_ids = {a.id for a in droner_accounts}
        if application.account_id not in droner_ids:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to delete this application",
            )
        self.application_repository.delete(application_id)
