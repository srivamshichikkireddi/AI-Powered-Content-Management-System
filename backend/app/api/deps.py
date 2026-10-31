from typing import Callable, List
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.errors import AICMSException
from backend.app.models.user import User
from backend.app.services.auth_service import validate_session_token


async def get_current_user(
    authorization: str = Header(None, description="Bearer <session_token>"),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Extract and validate server-side session token from Authorization header.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AICMSException(
            code="UNAUTHORIZED",
            message="Missing or invalid Bearer authentication token",
            status_code=401,
        )

    token = authorization.split("Bearer ", 1)[1].strip()
    return await validate_session_token(db, token)


def require_roles(*allowed_roles: str) -> Callable:
    """
    Role-Based Access Control (RBAC) dependency factory (satisfies AICMS-F-024, TC-ADM-03).
    Ensures user belongs to one of the authorized roles.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise AICMSException(
                code="FORBIDDEN_ROLE",
                message=f"Access denied. Required role in {allowed_roles}, but current role is '{current_user.role}'",
                status_code=403,
            )
        return current_user

    return role_checker
