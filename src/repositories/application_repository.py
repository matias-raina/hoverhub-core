from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.application import Application
from src.repositories.base_repository import BaseRepository


class ApplicationRepository(BaseRepository):
    def __init__(self, db_session: Session):
        super().__init__(db_session)
        self.model = Application

    def get_application_by_id(self, application_id: int) -> Optional[Application]:
        return self.get(self.model, application_id)

    def get_applications_by_account_id(self, account_id: int) -> List[Application]:
        return self.db_session.query(self.model).filter(self.model.account_id == account_id).all()

    def get_applications_by_job_id(self, job_id: int) -> List[Application]:
        return self.db_session.query(self.model).filter(self.model.job_id == job_id).all()

    def submit_application(self, application_data: dict) -> Application:
        new_application = Application(**application_data)
        return self.add(new_application)

    def update_application(self, application_id: int, updated_data: dict) -> Optional[Application]:
        application = self.get_application_by_id(application_id)
        if application:
            for key, value in updated_data.items():
                if hasattr(application, key):
                    setattr(application, key, value)
            self.db_session.commit()
            return application
        return None

    def delete_application(self, application_id: int) -> bool:
        application = self.get_application_by_id(application_id)
        if application:
            self.delete(application)
            return True
        return False

    def application_exists(self, job_id: int, account_id: int) -> bool:
        return self.db_session.query(self.model).filter(
            self.model.job_id == job_id,
            self.model.account_id == account_id
        ).count() > 0
