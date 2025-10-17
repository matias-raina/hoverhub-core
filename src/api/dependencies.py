from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from ..config.database import get_db
from ..services.auth_service import AuthService
from ..repositories.user_repository import UserRepository


def get_current_user(db: Session = Depends(get_db), token: str = Depends(AuthService.get_token_from_header)):
    user = AuthService.verify_token(token)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid authentication credentials")
    return user


def get_user_repository(db: Session = Depends(get_db)):
    return UserRepository(db)
