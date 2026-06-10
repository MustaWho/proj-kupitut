"""User endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers.dependencies import get_db
from app.models import User
from app.dto.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService

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


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: Annotated[Session, Depends(get_db)]) -> Response:
    """Delete a user."""

    await UserService(db).delete_user(user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
