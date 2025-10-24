from sqlalchemy.orm import Session
from typing import Optional, List
from src.models.notification import Notification
from src.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)
        self.model = Notification

    def get_notification_by_id(self, notification_id: int) -> Optional[Notification]:
        return self.get(self.model, notification_id)

    def get_notifications_by_user_id(self, user_id: int, unread_only: bool = False) -> List[Notification]:
        query = self.db_session.query(self.model).filter(self.model.recipient_user_id == user_id)
        if unread_only:
            query = query.filter(self.model.read_at.is_(None))
        return query.order_by(self.model.created_at.desc()).all()

    def create_notification(self, notification_data: dict) -> Notification:
        notification = Notification(**notification_data)
        return self.add(notification)

    def mark_as_read(self, notification_id: int) -> Optional[Notification]:
        from datetime import datetime
        notification = self.get(self.model, notification_id)
        if notification and notification.read_at is None:
            notification.read_at = datetime.utcnow()
            self.db_session.commit()
            return notification
        return None

    def mark_all_as_read(self, user_id: int) -> bool:
        from datetime import datetime
        notifications = self.db_session.query(self.model).filter(
            self.model.recipient_user_id == user_id,
            self.model.read_at.is_(None)
        ).all()
        for notification in notifications:
            notification.read_at = datetime.utcnow()
        self.db_session.commit()
        return True

    def delete_notification(self, notification_id: int) -> bool:
        notification = self.get(self.model, notification_id)
        if notification:
            self.delete(notification)
            return True
        return False

    def get_unread_count(self, user_id: int) -> int:
        return self.db_session.query(self.model).filter(
            self.model.recipient_user_id == user_id,
            self.model.read_at.is_(None)
        ).count()
