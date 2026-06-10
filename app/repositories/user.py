"""User CRUD operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User


class UserCRUD:
    """Persistence operations for users."""

    def get(self, db: Session, user_id: int) -> User | None:
        return db.get(User, user_id)

    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.scalar(select(User).where(User.email == email))

    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.scalar(select(User).where(User.username == username))

    def list(self, db: Session, offset: int = 0, limit: int = 100) -> list[User]:
        return list(db.scalars(select(User).order_by(User.id).offset(offset).limit(limit)))

    def create(self, db: Session, values: dict[str, object]) -> User:
        user = User(**values)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def update(self, db: Session, user: User, values: dict[str, object]) -> User:
        for field, value in values.items():
            setattr(user, field, value)
        db.commit()
        db.refresh(user)
        return user

    def delete(self, db: Session, user: User) -> None:
        db.delete(user)
        db.commit()


user_crud = UserCRUD()
