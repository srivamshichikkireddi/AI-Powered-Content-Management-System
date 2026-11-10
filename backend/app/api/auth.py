from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import get_current_user
from backend.app.core.database import get_db
from backend.app.core.errors import AICMSException
from backend.app.models.user import User
from backend.app.schemas.auth import LoginRequest, LogoutResponse, TokenResponse
from backend.app.schemas.user import UserResponse
from backend.app.services.auth_service import authenticate_user, revoke_session

router = APIRouter(prefix="/auth", tags=["Authentication & Sessions"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Authenticate user credentials, enforce 5-failure lockout (SR-008),
    and issue a server-side session token with 30-min idle timeout (SR-008, TC-SEC-07/08/09).
    """
    client_ip = request.client.host if request.client else None
    session, user = await authenticate_user(
        db=db,
        username=payload.username,
        password=payload.password,
        ip_address=client_ip,
    )
    return TokenResponse(
        access_token=session.session_token,
        token_type="bearer",
        expires_in=1800,
        user=UserResponse.model_validate(user),
    )


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    authorization: str = Header(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> LogoutResponse:
    """
    Revoke server-side session token so it cannot be reused (satisfies TC-SEC-09).
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise AICMSException(code="UNAUTHORIZED", message="Invalid token", status_code=401)

    token = authorization.split("Bearer ", 1)[1].strip()
    await revoke_session(db, token, current_user)
    return LogoutResponse(status="logged_out", message="Session invalidated successfully")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get active user profile and assigned role."""
    return UserResponse.model_validate(current_user)
