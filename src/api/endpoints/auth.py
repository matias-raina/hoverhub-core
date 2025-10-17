from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.schemas.user_schema import UserCreate
from src.services.auth_service import AuthService
from src.api.dependencies import get_user_repository

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_user_repository)):
    service = AuthService(db)
    return service.login(email, password)

@router.post("/register")
def register(user_data: UserCreate, db: Session = Depends(get_user_repository)):
    service = AuthService(db)
    return service.register(user_data)

@router.post("/logout")
def logout(token: str, db: Session = Depends(get_user_repository)):
    service = AuthService(db)
    return service.logout(token)
