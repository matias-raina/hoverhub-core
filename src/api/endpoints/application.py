from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.services.application_service import ApplicationService
from src.api.dependencies import get_current_user, get_user_repository

router = APIRouter(prefix="/applications", tags=["Applications"])

@router.post("/{offer_id}")
def apply_to_offer(offer_id: int, db: Session = Depends(get_user_repository), user=Depends(get_current_user)):
    service = ApplicationService(db)
    return service.apply_to_offer(offer_id, user)

@router.delete("/{application_id}")
def withdraw_application(application_id: int, db: Session = Depends(get_user_repository), user=Depends(get_current_user)):
    service = ApplicationService(db)
    return service.withdraw_application(application_id, user)
