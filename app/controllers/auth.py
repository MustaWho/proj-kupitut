"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.controllers.dependencies import get_db
from app.dto.auth import (
    AuthResponse,
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
)
from app.services.auth_service import AuthService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    db: Annotated[Session, Depends(get_db)],
) -> AuthResponse:
    """Register and authenticate a new user."""

    user, access_token, refresh_token = await AuthService(db).register(payload)
    return AuthResponse(user=user, access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]) -> AuthResponse:
    """Authenticate by email or username."""

    user, access_token, refresh_token = await AuthService(db).login(payload)
    return AuthResponse(user=user, access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: Annotated[Session, Depends(get_db)]) -> TokenPair:
    """Refresh access and refresh tokens."""

    access_token, refresh_token = await AuthService(db).refresh(payload)
    return TokenPair(access_token=access_token, refresh_token=refresh_token)


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: ChangePasswordRequest,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """Change password and revoke existing refresh tokens."""

    await AuthService(db).change_password(payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
