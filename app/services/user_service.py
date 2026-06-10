"""User business logic."""

from sqlalchemy.orm import Session

from app.security import hash_password
from app.repositories.user import user_crud
from app.models import User
from app.dto.user import UserCreate, UserUpdate
from app.utils.exceptions import ConflictError, NotFoundError


class UserService:
    """Use cases for users."""

    def __init__(self, db: Session):
        self.db = db

    async def create_user(self, payload: UserCreate) -> User:
        if user_crud.get_by_email(self.db, str(payload.email)):
            raise ConflictError("Эта почта уже зарегистрирована")
        if user_crud.get_by_username(self.db, payload.username):
            raise ConflictError("Этот логин уже занят")

        values = payload.model_dump(exclude={"password"})
        values["email"] = str(payload.email)
        values["password_hash"] = hash_password(payload.password)
        return user_crud.create(self.db, values)

    async def list_users(self, offset: int = 0, limit: int = 100) -> list[User]:
        return user_crud.list(self.db, offset=offset, limit=limit)

    async def get_user(self, user_id: int) -> User:
        user = user_crud.get(self.db, user_id)
        if user is None:
            raise NotFoundError("Пользователь не найден")
        return user

    async def update_user(self, user_id: int, payload: UserUpdate) -> User:
        user = await self.get_user(user_id)
        values = payload.model_dump(exclude_unset=True)

        if "email" in values:
            values["email"] = str(values["email"])
            existing = user_crud.get_by_email(self.db, values["email"])
            if existing and existing.id != user_id:
                raise ConflictError("Эта почта уже зарегистрирована")

        if "username" in values:
            existing = user_crud.get_by_username(self.db, values["username"])
            if existing and existing.id != user_id:
                raise ConflictError("Этот логин уже занят")

        if "password" in values:
            values["password_hash"] = hash_password(str(values.pop("password")))

        return user_crud.update(self.db, user, values)

    async def delete_user(self, user_id: int) -> None:
        user = await self.get_user(user_id)
        user_crud.delete(self.db, user)
