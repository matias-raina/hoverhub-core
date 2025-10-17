from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.services.notification_service import NotificationService
from src.api.dependencies import get_current_user, get_user_repository


class NotificationRouter:
    def __init__(self):
        self.router = APIRouter()

        self.router.add_api_route(
            "/", self.send_notification, methods=["POST"])
        self.router.add_api_route("/", self.get_notifications, methods=["GET"])

    async def send_notification(self, receiver_id: int, message: str, db: Session = Depends(get_user_repository), sender=Depends(get_current_user)):
        service = NotificationService(db)
        return service.send_notification(sender, receiver_id, message)

    async def get_notifications(self, db: Session = Depends(get_user_repository), user=Depends(get_current_user)):
        service = NotificationService(db)
        return service.get_notifications(user.id)


notification_router = NotificationRouter().router
