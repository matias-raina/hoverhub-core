from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from pwdlib import PasswordHash
from sqlmodel import Session

from app.domain.models.account import Account, AccountType
from app.domain.models.application import Application, ApplicationStatus
from app.domain.models.favorite import Favorite
from app.domain.models.job import Job
from app.domain.models.session import UserSession
from app.domain.models.user import User

# Password hasher for creating test users
_password_hasher = PasswordHash.recommended()


def create_test_user(
    session: Session,
    email: str = "test@example.com",
    password: str = "testpassword123",
    is_active: bool = True,
) -> User:
    """
    Create a test user in the database.

    Args:
        session: Database session
        email: User email
        password: Plain text password (will be hashed)
        is_active: Whether user is active

    Returns:
        Created User instance
    """
    hashed_password = _password_hasher.hash(password)
    user = User(
        email=email,
        hashed_password=hashed_password,
        is_active=is_active,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_test_account(
    session: Session,
    user_id: UUID,
    name: str = "Test Account",
    account_type: AccountType = AccountType.DRONER,
    is_active: bool = True,
) -> Account:
    """
    Create a test account in the database.

    Args:
        session: Database session
        user_id: Owner user ID
        name: Account name
        account_type: DRONER or EMPLOYER
        is_active: Whether account is active

    Returns:
        Created Account instance
    """
    account = Account(
        user_id=user_id,
        name=name,
        account_type=account_type,
        is_active=is_active,
    )
    session.add(account)
    session.commit()
    session.refresh(account)
    return account


def create_test_job(
    session: Session,
    account_id: UUID,
    title: str = "Test Job",
    description: str = "Test job description",
    budget: float = 1000.0,
    location: str = "Test Location",
    start_date: date | None = None,
    end_date: date | None = None,
) -> Job:
    """
    Create a test job in the database.

    Args:
        session: Database session
        account_id: Account that owns the job
        title: Job title
        description: Job description
        budget: Job budget
        location: Job location
        start_date: Job start date (defaults to tomorrow)
        end_date: Job end date (defaults to 7 days from start)

    Returns:
        Created Job instance
    """
    if start_date is None:
        start_date = date.today() + timedelta(days=1)
    if end_date is None:
        end_date = start_date + timedelta(days=7)

    job = Job(
        account_id=account_id,
        title=title,
        description=description,
        budget=budget,
        location=location,
        start_date=start_date,
        end_date=end_date,
    )
    session.add(job)
    session.commit()
    session.refresh(job)
    return job


def create_test_session(
    session: Session,
    user_id: UUID,
    host: str = "127.0.0.1",
    is_active: bool = True,
    expires_at: datetime | None = None,
) -> UserSession:
    """
    Create a test user session in the database.

    Args:
        session: Database session
        user_id: User ID
        host: Client host/IP
        is_active: Whether session is active
        expires_at: Session expiration (defaults to 24 hours from now)

    Returns:
        Created UserSession instance
    """
    if expires_at is None:
        expires_at = datetime.now(UTC) + timedelta(hours=24)

    user_session = UserSession(
        user_id=user_id,
        host=host,
        is_active=is_active,
        expires_at=expires_at,
    )
    session.add(user_session)
    session.commit()
    session.refresh(user_session)
    return user_session


def create_test_application(
    session: Session,
    job_id: UUID,
    account_id: UUID,
    message: str | None = None,
    status: ApplicationStatus = ApplicationStatus.PENDING,
) -> Application:
    """
    Create a test application in the database.

    Args:
        session: Database session
        job_id: Job being applied to
        account_id: Account applying (must be DRONER type)
        message: Optional application message
        status: Application status

    Returns:
        Created Application instance
    """
    application = Application(
        job_id=job_id,
        account_id=account_id,
        message=message,
        status=status,
    )
    session.add(application)
    session.commit()
    session.refresh(application)
    return application


def create_test_favorite(
    session: Session,
    account_id: UUID,
    job_id: UUID,
) -> Favorite:
    """
    Create a test favorite in the database.

    Args:
        session: Database session
        account_id: Account that favorited the job
        job_id: Job being favorited

    Returns:
        Created Favorite instance
    """
    favorite = Favorite(
        account_id=account_id,
        job_id=job_id,
    )
    session.add(favorite)
    session.commit()
    session.refresh(favorite)
    return favorite


def get_auth_headers(token: str) -> dict:
    """
    Get authorization headers for authenticated requests.

    Args:
        token: JWT access token

    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {token}"}


def get_account_headers(token: str, account_id: UUID) -> dict:
    """
    Get authorization headers with account context for requests requiring x-account-id.

    Args:
        token: JWT access token
        account_id: Account ID for context

    Returns:
        Dictionary with Authorization and x-account-id headers
    """
    return {
        "Authorization": f"Bearer {token}",
        "x-account-id": str(account_id),
    }
