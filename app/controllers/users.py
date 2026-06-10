"""User endpoints."""

from typing import Annotated
from pathlib import Path

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.config import settings
from app.controllers.dependencies import get_db
from app.models import User
from app.dto.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService
from app.utils.images import save_replaced_image

router = APIRouter()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: Annotated[Session, Depends(get_db)]) -> User:
    """Create a user."""

    return await UserService(db).create_user(payload)


@router.get("", response_model=list[UserRead])
async def list_users(
    db: Annotated[Session, Depends(get_db)],
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[User]:
    """List users."""

    return await UserService(db).list_users(offset=offset, limit=limit)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]) -> User:
    """Get a user by id."""

    return await UserService(db).get_user(user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Update a user."""

    return await UserService(db).update_user(user_id, payload)


@router.post("/{user_id}/avatar", response_model=UserRead)
async def upload_avatar(
    user_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Upload or replace a user's avatar image."""

    service = UserService(db)
    await service.get_user(user_id)
    avatar_url = save_replaced_image(
        content=await request.body(),
        content_type=request.headers.get("content-type"),
        directory=Path(settings.media_dir) / "avatars",
        file_stem=f"user_{user_id}",
        public_prefix="/media/avatars",
    )
    return await service.update_avatar(user_id, avatar_url)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]) -> Response:
    """Delete a user."""

    await UserService(db).delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
