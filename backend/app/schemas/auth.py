from typing import Optional
from pydantic import BaseModel, Field

from backend.app.schemas.user import UserResponse


class LoginRequest(BaseModel):
    username: str = Field(..., description="Registered username")
    password: str = Field(..., description="Account password")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="Opaque cryptographically secure session token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(1800, description="Session idle expiration in seconds (30 minutes)")
    user: UserResponse


class LogoutResponse(BaseModel):
    status: str = "logged_out"
    message: str = "Session invalidated successfully"
