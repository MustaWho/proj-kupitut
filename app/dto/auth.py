"""Authentication schemas."""

from pydantic import EmailStr, Field

from app.dto.base import ORMBaseModel
from app.dto.user import UserCreate, UserRead


class RegisterRequest(UserCreate):
    """Register user payload."""


class LoginRequest(ORMBaseModel):
    """Login payload."""

    login: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=128)


class TokenPair(ORMBaseModel):
    """Access and refresh token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(TokenPair):
    """Authentication response with user data."""

    user: UserRead


class RefreshRequest(ORMBaseModel):
    """Refresh access token payload."""

    refresh_token: str = Field(min_length=20)


class ChangePasswordRequest(ORMBaseModel):
    """Change password payload."""

    email: EmailStr
    old_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
