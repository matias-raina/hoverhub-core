from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.user_schema import UserCreate, UserUpdate
from src.services.user_service import UserService
from src.api.dependencies import get_current_user, get_user_repository
from src.models.user_model import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_user_repository)):
    service = UserService(db)
    return service.get_profile(user_id)

@router.put("/{user_id}")
def update_profile(user_id: int, user_data: UserUpdate, db: Session = Depends(get_user_repository)):
    service = UserService(db)
    return service.update_profile(user_id, user_data)

@router.put("/{user_id}/password")
def change_password(user_id: int, current: str, new: str, db: Session = Depends(get_user_repository)):
    service = UserService(db)
    return service.change_password(user_id, current, new)
