from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.job_alert_subscription import JobAlertSubscription
from src.repositories.base_repository import BaseRepository


class JobAlertSubscriptionRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = JobAlertSubscription

    def get_subscription_by_id(self, subscription_id: int) -> Optional[JobAlertSubscription]:
        return self.get(self.model, subscription_id)

    def get_subscriptions_by_droner_account_id(self, droner_account_id: int, active_only: bool = True) -> List[JobAlertSubscription]:
        query = self.db_session.query(self.model).filter(
            self.model.droner_account_id == droner_account_id
        )
        if active_only:
            query = query.filter(self.model.is_active == True)
        return query.all()

    def get_subscriptions_by_category_id(self, job_category_id: int, active_only: bool = True) -> List[JobAlertSubscription]:
        query = self.db_session.query(self.model).filter(
            self.model.job_category_id == job_category_id
        )
        if active_only:
            query = query.filter(self.model.is_active == True)
        return query.all()

    def get_subscriptions_by_poster_account_id(self, job_poster_account_id: int, active_only: bool = True) -> List[JobAlertSubscription]:
        query = self.db_session.query(self.model).filter(
            self.model.job_poster_account_id == job_poster_account_id
        )
        if active_only:
            query = query.filter(self.model.is_active == True)
        return query.all()

    def create_subscription(self, subscription_data: dict) -> JobAlertSubscription:
        subscription = JobAlertSubscription(**subscription_data)
        return self.add(subscription)

    def update_subscription(self, subscription_id: int, subscription_data: dict) -> Optional[JobAlertSubscription]:
        subscription = self.get(self.model, subscription_id)
        if subscription:
            for key, value in subscription_data.items():
                if hasattr(subscription, key):
                    setattr(subscription, key, value)
            self.db_session.commit()
            return subscription
        return None

    def toggle_subscription(self, subscription_id: int) -> Optional[JobAlertSubscription]:
        subscription = self.get(self.model, subscription_id)
        if subscription:
            subscription.is_active = not subscription.is_active
            self.db_session.commit()
            return subscription
        return None

    def delete_subscription(self, subscription_id: int) -> bool:
        subscription = self.get(self.model, subscription_id)
        if subscription:
            self.delete(subscription)
            return True
        return False
