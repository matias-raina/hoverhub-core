from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

from src.utils.jwt_handler import JWTHandler
from src.config.settings import settings


class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_user_by_id(self, user_id: int):
        # return user or raise 404
        return self._get_user_or_404(user_id=user_id)
        
    def get_user_by_email(self, email: str):
        # return user or raise 404
        return self._get_user_or_404(email=email)


    def create_user(self, user_data):
        # validate full payload for creation
        self.validate_user_data(user_data, partial=False)
        user_data['password'] = self.hash_password(user_data['password'])
        return self.user_repository.create_user(user_data)

    def update_user(self, user_id: str, **kwargs):
        """Update user information."""
        user = self._get_user_or_404(user_id=user_id)

        # Update allowed fields
        if "email" in kwargs:
            user.email = kwargs["email"]

        user.updated_at = datetime.now(timezone.utc)
        return self.user_repository.update(user)
       

    def delete_user(self, user_id: int):
        # ensure user exists
        self._get_user_or_404(user_id=user_id)
        return self.user_repository.delete_user(user_id)

    def hash_password(self, password: str) -> str:
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    def validate_user_data(self, user_data: Dict[str, Any], partial: bool = False):
        """
        Validate user input. If partial=True, only validate fields present in user_data.
        """
        from utils.validators import validate_email, validate_password, validate_username

        if not partial or 'email' in user_data:
            if not validate_email(user_data.get('email', '')):
                raise ValueError("Invalid email format.")

        if not partial or 'password' in user_data:
            # when partial and password not provided, skip
            if 'password' in user_data and not validate_password(user_data.get('password', '')):
                raise ValueError("Password does not meet security criteria.")

        if not partial or 'username' in user_data:
            if not validate_username(user_data.get('username', '')):
                raise ValueError("Username must be between 3 and 30 characters.")

    def authenticate(self, email: str, password: str):
        # avoid raising 404 on login attempts to prevent user enumeration
        user = self.user_repository.get_user_by_email(email)
        if not user:
            return None
        # model returned by repository likely is SQLAlchemy model
        if self.hash_password(password) != getattr(user, 'password'):
            return None

        payload = {
            "sub": str(getattr(user, 'id')),
            "email": getattr(user, 'email')
        }

        # create token with configured expiry
        expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = JWTHandler.encode_jwt(payload, expires)

        # sanitize user when returning (don't leak password)
        try:
            user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
            user_dict.pop('password', None)
        except Exception:
            # fallback: return minimal info
            user_dict = {
                "id": getattr(user, 'id'), 
                "email": getattr(user, 'email'), 
                "username": getattr(user, 'username', None)
            }

        return {"access_token": token, "token_type": "bearer", "user": user_dict}
    
    def change_password(self, user_id: int, current_password: str, new_password: str):
        from utils.validators import validate_password
        if not validate_password(new_password):
            raise ValueError("New password does not meet security criteria.")

        user = self._get_user_or_404(user_id=user_id)
        # compare against model attribute
        if self.hash_password(current_password) != getattr(user, 'password'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password incorrect"
            )

        new_hashed = self.hash_password(new_password)
        return self.user_repository.update_user(user_id, {'password': new_hashed})

    def is_email_available(self, email: str) -> bool:
        # check repository directly to avoid raising 404
        return self.user_repository.get_user_by_email(email) is None


    def deactivate(self, user_id: int):
        user = self._get_user_or_404(user_id=user_id)
        return self.user_repository.update_user(user_id, {'is_active': False})

    def activate(self, user_id: int):
        user = self._get_user_or_404(user_id=user_id)
        return self.user_repository.update_user(user_id, {'is_active': True})
    
    def _get_user_or_404(self, user_id: Optional[int] = None, email: Optional[str] = None):
        """Return the user model if exists or raise HTTPException(404).

        Either user_id or email must be provided.
        """
        if user_id is None and email is None:
            raise ValueError("Either 'user_id' or 'email' must be provided")

        if email is not None:
            user = self.user_repository.get_user_by_email(email)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"User with email {email} not found"
                )
            return user

        user = self.user_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return user