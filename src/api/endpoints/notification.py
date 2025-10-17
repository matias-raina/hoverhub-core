from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.services.notification_service import NotificationService
from src.api.dependencies import get_current_user, get_user_repository

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/")
def send_notification(receiver_id: int, message: str, db: Session = Depends(get_user_repository), sender=Depends(get_current_user)):
    service = NotificationService(db)
    return service.send_notification(sender, receiver_id, message)

@router.get("/")
def get_notifications(db: Session = Depends(get_user_repository), user=Depends(get_current_user)):
    service = NotificationService(db)
    return service.get_notifications(user.id)
