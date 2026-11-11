from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$", description="Valid email address")
    role: str = Field("user", description="Role: admin, editor, user, auditor")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Minimum 8 characters password")


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    failed_login_attempts: int
    locked_until: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: str = Field(..., description="Target role: admin, editor, user, auditor")
