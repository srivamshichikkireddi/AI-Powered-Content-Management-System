from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import require_roles
from backend.app.core.database import get_db
from backend.app.core.errors import AICMSException
from backend.app.core.security import get_password_hash
from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserResponse, UserRoleUpdate

router = APIRouter(prefix="/users", tags=["User Administration (Admin Only)"])


@router.get("", response_model=List[UserResponse])
async def list_users(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> List[UserResponse]:
    """
    List all users in the system (Admin only, TC-ADM-03).
    """
    stmt = select(User).order_by(User.id)
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [UserResponse.model_validate(u) for u in users]


@router.post("", response_model=UserResponse, status_code=201)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> UserResponse:
    """Create a new user with assigned role (Admin only)."""
    # Check duplicate username
    stmt = select(User).where((User.username == payload.username) | (User.email == payload.email))
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise AICMSException(code="USER_EXISTS", message="Username or email already exists", status_code=409)

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_roles("admin")),
) -> UserResponse:
    """Change role of a user (Admin only, TC-ADM-03)."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise AICMSException(code="NOT_FOUND", message="User not found", status_code=404)

    user.role = payload.role
    await db.commit()
    await db.refresh(user)
    return UserResponse.model_validate(user)
