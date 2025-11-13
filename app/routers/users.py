from fastapi import APIRouter, status

from app.config.dependencies import AuthenticatedUserDep, UserServiceDep

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user(authenticated_user: AuthenticatedUserDep):
    return {
        "id": authenticated_user.id,
        "email": authenticated_user.email,
        "is_active": authenticated_user.is_active,
        "created_at": authenticated_user.created_at,
    }


@router.get("/sessions", status_code=status.HTTP_200_OK)
async def get_user_sessions(authenticated_user: AuthenticatedUserDep, user_service: UserServiceDep):
    """
    Get all sessions for the authenticated user.
    """
    sessions = user_service.get_user_sessions(authenticated_user.id)

    return [
        {
            "id": session.id,
            "user_id": session.user_id,
            "host": session.host,
            "is_active": session.is_active,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
        }
        for session in sessions
    ]
