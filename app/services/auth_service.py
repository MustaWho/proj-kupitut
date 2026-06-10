"""Authentication business logic."""

import secrets

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.dto.auth import ChangePasswordRequest, LoginRequest, RefreshRequest, RegisterRequest
from app.models import RefreshToken, User
from app.repositories.user import user_crud
from app.security import create_token, hash_password, verify_password
from app.services.user_service import UserService
from app.utils.exceptions import BadRequestError, NotFoundError


class AuthService:
    """Use cases for registration and authentication."""

    def __init__(self, db: Session):
        self.db = db

    async def register(self, payload: RegisterRequest) -> tuple[User, str, str]:
        user = await UserService(self.db).create_user(payload)
        return user, self._create_access_token(user), self._create_refresh_token(user)

    async def login(self, payload: LoginRequest) -> tuple[User, str, str]:
        user = user_crud.get_by_email(self.db, payload.login)
        if user is None:
            user = user_crud.get_by_username(self.db, payload.login.lower())
        if user is None or not verify_password(payload.password, user.password_hash):
            raise BadRequestError("Неверный логин или пароль")
        if not user.is_active:
            raise BadRequestError("Пользователь отключён")
        return user, self._create_access_token(user), self._create_refresh_token(user)

    async def refresh(self, payload: RefreshRequest) -> tuple[str, str]:
        token = self.db.scalar(
            select(RefreshToken).where(
                RefreshToken.token == payload.refresh_token,
                RefreshToken.is_revoked.is_(False),
            )
        )
        if token is None:
            raise BadRequestError("Refresh-токен недействителен")
        user = self.db.get(User, token.user_id)
        if user is None or not user.is_active:
            raise NotFoundError("Пользователь не найден")
        token.is_revoked = True
        self.db.commit()
        return self._create_access_token(user), self._create_refresh_token(user)

    async def change_password(self, payload: ChangePasswordRequest) -> None:
        user = user_crud.get_by_email(self.db, str(payload.email))
        if user is None:
            raise NotFoundError("Пользователь не найден")
        if not verify_password(payload.old_password, user.password_hash):
            raise BadRequestError("Старый пароль указан неверно")
        user.password_hash = hash_password(payload.new_password)
        for token in user.refresh_tokens:
            token.is_revoked = True
        self.db.commit()

    def _create_access_token(self, user: User) -> str:
        return create_token(str(user.id), settings.token_secret, settings.access_token_seconds)

    def _create_refresh_token(self, user: User) -> str:
        token_value = secrets.token_urlsafe(48)
        refresh_token = RefreshToken(user_id=user.id, token=token_value)
        self.db.add(refresh_token)
        self.db.commit()
        return token_value
