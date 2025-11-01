"""Authentication middleware for JWT token validation."""

from typing import Callable, Optional

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.domain.repositories.auth import AuthRepository


class AuthenticationMiddleware(BaseHTTPMiddleware):

    def __init__(
        self, app, auth_repository: AuthRepository, public_paths: Optional[list] = None
    ):

        super().__init__(app)
        self.auth_repository = auth_repository

        # Default public paths that don't require authentication
        self.public_paths = public_paths or [
            "/auth/signin",
            "/auth/signup",
            "/auth/token",
            "/auth/signout",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and validate authentication if required.

        Args:
            request: Incoming HTTP request
            call_next: Next middleware or route handler

        Returns:
            HTTP response
        """
        # Skip authentication for public paths
        if self._is_public_path(request.url.path):
            return await call_next(request)

        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")

        if not authorization:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Missing authorization header",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate Bearer token format
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={
                    "detail": "Invalid authorization header format. Expected: Bearer <token>",
                },
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = parts[1]

        # Validate the token
        try:
            payload = self.auth_repository.decode_token(token)
            # Attach the decoded payload to request state for use in route handlers
            request.state.user_payload = payload
        except HTTPException as exc:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": exc.detail},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Continue to the next middleware or route handler
        response = await call_next(request)
        return response

    def _is_public_path(self, path: str) -> bool:
        """
        Check if a path is public (doesn't require authentication).

        Args:
            path: Request path

        Returns:
            True if path is public, False otherwise
        """
        return any(path.startswith(public_path) for public_path in self.public_paths)
