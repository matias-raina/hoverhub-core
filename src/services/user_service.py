from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status

from src.utils.jwt_handler import JWTHandler
from src.config.settings import settings

class UserService:
    def __init__(self, user_repository,
                 account_repository=None,
                 notification_repository=None,
                 favorite_repository=None,
                 application_repository=None,
                 job_alert_subscription_repository=None,
                 email_service=None):
        self.user_repository = user_repository
        self.account_repository = account_repository
        self.notification_repository = notification_repository
        self.favorite_repository = favorite_repository
        self.application_repository = application_repository
        self.job_alert_subscription_repository = job_alert_subscription_repository
        self.email_service = email_service

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
        created = self.user_repository.create_user(user_data)
        try:
            return self._serialize_user(created)
        except Exception:
            return created

    def update_user(self, user_id: str, **kwargs):
        """Update user information."""
        user = self._get_user_or_404(user_id=user_id)

        # Update allowed fields
        if "email" in kwargs:
            user.email = kwargs["email"]

        user.updated_at = datetime.now(timezone.utc)
        updated = self.user_repository.update(user)
        try:
            return self._serialize_user(updated)
        except Exception:
            return updated

    def get_profile(self, current_user):
        """Return sanitized profile for current_user.

        current_user may be a model instance or an id.
        """
        # accept either model or id
        if hasattr(current_user, 'id'):
            user = current_user
        else:
            user = self._get_user_or_404(user_id=current_user)

        return self._serialize_user(user)

    def update_profile(self, current_user, profile_data: Dict[str, Any]):
        """Update profile fields for current_user (partial)."""
        # accept model or id
        if hasattr(current_user, 'id'):
            user_id = getattr(current_user, 'id')
        else:
            user_id = current_user

        # validate only provided fields
        self.validate_user_data(profile_data, partial=True)
        if 'password' in profile_data and profile_data.get('password'):
            profile_data['password'] = self.hash_password(profile_data['password'])

        return self.user_repository.update_user(user_id, profile_data)

    def get_accounts_for_user(self, user_id: int):
        """Return accounts for a given user. Ensures user exists."""
        self._get_user_or_404(user_id=user_id)
        if not self.account_repository:
            raise NotImplementedError("Account repository not provided to UserService")
        return self.account_repository.get_accounts_by_user_id(user_id)

    def list_users(self, page: int = 1, per_page: int = 20, filters: dict = None):
        """Simple listing with in-memory filtering/pagination using repository get_all_users()."""
        users = self.user_repository.get_all_users()
        # apply simple filters (username/email substrings)
        if filters:
            if 'email' in filters:
                users = [u for u in users if filters['email'].lower() in getattr(u, 'email', '').lower()]
            if 'username' in filters:
                users = [u for u in users if filters['username'].lower() in getattr(u, 'username', '').lower()]

        # pagination (1-based)
        start = (page - 1) * per_page
        end = start + per_page
        paged = users[start:end]
        return [self._serialize_user(u) for u in paged]

    def list_notifications(self, user_identifier, unread_only: bool = False):
        """List notifications for a user (accepts id or model)."""
        if not self.notification_repository:
            raise NotImplementedError("Notification repository not provided to UserService")
        if hasattr(user_identifier, 'id'):
            user_id = getattr(user_identifier, 'id')
        else:
            user_id = user_identifier
        # ensure user exists
        self._get_user_or_404(user_id=user_id)
        return self.notification_repository.get_notifications_by_user_id(user_id, unread_only=unread_only)

    def mark_notification_read(self, notification_id: int):
        if not self.notification_repository:
            raise NotImplementedError("Notification repository not provided to UserService")
        return self.notification_repository.mark_as_read(notification_id)

    def list_favorites(self, account_identifier):
        """List favorites for an account or for the first account of a user model/id."""
        if not self.favorite_repository:
            raise NotImplementedError("Favorite repository not provided to UserService")
        # accept account id or user model/id
        if hasattr(account_identifier, 'id') and getattr(account_identifier, 'user_id', None) is None:
            # looks like an Account model
            account_id = getattr(account_identifier, 'id')
        elif hasattr(account_identifier, 'id') and getattr(account_identifier, 'user_id', None) is not None:
            # user model passed; get accounts
            if not self.account_repository:
                raise NotImplementedError("Account repository not provided to UserService")
            accounts = self.account_repository.get_accounts_by_user_id(getattr(account_identifier, 'id'))
            account_id = accounts[0].id if accounts else None
        else:
            # assume it's an account id or user id (int)
            # try to resolve as account id first
            account_id = account_identifier
            # if account id doesn't return favorites, caller can pass account id explicitly

        if account_id is None:
            return []
        return self.favorite_repository.get_favorites_by_account_id(account_id)

    def list_applications(self, account_identifier):
        if not self.application_repository:
            raise NotImplementedError("Application repository not provided to UserService")
        # accept account id or user model/id -> resolve to account id
        if hasattr(account_identifier, 'id') and getattr(account_identifier, 'user_id', None) is not None:
            # user model passed
            if not self.account_repository:
                raise NotImplementedError("Account repository not provided to UserService")
            accounts = self.account_repository.get_accounts_by_user_id(getattr(account_identifier, 'id'))
            account_id = accounts[0].id if accounts else None
        elif hasattr(account_identifier, 'id') and getattr(account_identifier, 'user_id', None) is None:
            # account model
            account_id = getattr(account_identifier, 'id')
        else:
            account_id = account_identifier

        if account_id is None:
            return []
        return self.application_repository.get_applications_by_account_id(account_id)

    def subscribe_job_alert(self, subscription_data: dict):
        if not self.job_alert_subscription_repository:
            raise NotImplementedError("JobAlertSubscription repository not provided to UserService")
        return self.job_alert_subscription_repository.create_subscription(subscription_data)

    def unsubscribe_job_alert(self, subscription_id: int):
        if not self.job_alert_subscription_repository:
            raise NotImplementedError("JobAlertSubscription repository not provided to UserService")
        return self.job_alert_subscription_repository.delete_subscription(subscription_id)

    def reset_password_request(self, email: str):
        """Generate a short-lived JWT reset token and optionally send email via EmailService.

        Note: persistence of tokens is not implemented here; token is self-contained JWT.
        """
        user = self.user_repository.get_user_by_email(email)
        if not user:
            # do not reveal existence; behave idempotently
            return True

        payload = {"sub": str(getattr(user, 'id')), "email": getattr(user, 'email'), "type": "reset"}
        expires = timedelta(minutes=30)
        token = JWTHandler.encode_jwt(payload, expires)
        if self.email_service and hasattr(self.email_service, 'send_reset_email'):
            try:
                self.email_service.send_reset_email(getattr(user, 'email'), token)
            except Exception:
                # swallow email errors here; caller can retry
                pass
        return token

    def reset_password(self, token: str, new_password: str):
        """Validate reset token (JWT) and update the user's password."""
        try:
            payload = JWTHandler.decode_jwt(token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

        if payload.get('type') != 'reset':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type")

        email = payload.get('email')
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        from utils.validators import validate_password
        if not validate_password(new_password):
            raise ValueError("New password does not meet security criteria.")

        new_hashed = self.hash_password(new_password)
        return self.user_repository.update_user(getattr(user, 'id'), {'password': new_hashed})

    def verify_email_request(self, email: str):
        user = self.user_repository.get_user_by_email(email)
        if not user:
            return True
        payload = {"sub": str(getattr(user, 'id')), "email": getattr(user, 'email'), "type": "verify"}
        expires = timedelta(hours=24)
        token = JWTHandler.encode_jwt(payload, expires)
        if self.email_service and hasattr(self.email_service, 'send_verification_email'):
            try:
                self.email_service.send_verification_email(getattr(user, 'email'), token)
            except Exception:
                pass
        return token

    def verify_email(self, token: str):
        try:
            payload = JWTHandler.decode_jwt(token)
        except Exception:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")
        if payload.get('type') != 'verify':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token type")
        email = payload.get('email')
        user = self.user_repository.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        # try to set 'is_verified' flag if model has it
        try:
            return self.user_repository.update_user(getattr(user, 'id'), {'is_verified': True})
        except Exception:
            # repository may not support this field
            return None
    
    def _serialize_user(self, user):
        """Serialize a SQLAlchemy user model to dict and remove sensitive fields."""
        try:
            user_dict = {c.name: getattr(user, c.name) for c in user.__table__.columns}
            user_dict.pop('password', None)
            return user_dict
        except Exception:
            return {"id": getattr(user, 'id', None), "email": getattr(user, 'email', None), "username": getattr(user, 'username', None)}
       

    def delete_user(self, user_id: int):
        # ensure user exists
        self._get_user_or_404(user_id=user_id)
        return self.user_repository.delete_user(user_id)

    def hash_password(self, password: str) -> str:
        # Use bcrypt for password hashing (safer than plain sha256)
        import bcrypt
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        return hashed.decode()

    def verify_password(self, password: str, hashed: str) -> bool:
        import bcrypt
        try:
            return bcrypt.checkpw(password.encode(), hashed.encode())
        except Exception:
            return False

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
        if not self.verify_password(password, getattr(user, 'password')):
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
        if not self.verify_password(current_password, getattr(user, 'password')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password incorrect"
            )

        new_hashed = self.hash_password(new_password)
        updated = self.user_repository.update_user(user_id, {'password': new_hashed})
        try:
            return self._serialize_user(updated)
        except Exception:
            return updated

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