"""Task and tag CRUD operations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Tag, Task


class TaskCRUD:
    """Persistence operations for tasks and tags."""

    def get(self, db: Session, task_id: int) -> Task | None:
        return db.scalar(select(Task).options(selectinload(Task.tags)).where(Task.id == task_id))

    def list_tasks(
        self,
        db: Session,
        project_id: int | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Task]:
        query = select(Task).options(selectinload(Task.tags)).order_by(Task.id)
        if project_id is not None:
            query = query.where(Task.project_id == project_id)
        if status is not None:
            query = query.where(Task.status == status)
        query = query.offset(offset).limit(limit)
        return list(db.scalars(query))

    def get_tag_by_name(self, db: Session, name: str) -> Tag | None:
        return db.scalar(select(Tag).where(Tag.name == name))

    def get_or_create_tags(self, db: Session, names: list[str]) -> list[Tag]:
        tags: list[Tag] = []
        for name in names:
            tag = self.get_tag_by_name(db, name)
            if tag is None:
                tag = Tag(name=name)
                db.add(tag)
                db.flush()
            tags.append(tag)
        return tags

    def create(self, db: Session, values: dict[str, object], tags: list[Tag]) -> Task:
        task = Task(**values)
        task.tags = tags
        db.add(task)
        db.commit()
        db.refresh(task)
        return self.get(db, task.id) or task

    def update(
        self,
        db: Session,
        task: Task,
        values: dict[str, object],
        tags: list[Tag] | None = None,
    ) -> Task:
        for field, value in values.items():
            setattr(task, field, value)
        if tags is not None:
            task.tags = tags
        db.commit()
        db.refresh(task)
        return self.get(db, task.id) or task

    def delete(self, db: Session, task: Task) -> None:
        db.delete(task)
        db.commit()


task_crud = TaskCRUD()
