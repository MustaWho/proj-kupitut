"""Project CRUD operations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Project


class ProjectCRUD:
    """Persistence operations for projects."""

    def get(self, db: Session, project_id: int) -> Project | None:
        return db.get(Project, project_id)

    def get_by_owner_and_name(self, db: Session, owner_id: int, name: str) -> Project | None:
        return db.scalar(select(Project).where(Project.owner_id == owner_id, Project.name == name))

    def list(
        self,
        db: Session,
        owner_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        query = select(Project).order_by(Project.id).offset(offset).limit(limit)
        if owner_id is not None:
            query = query.where(Project.owner_id == owner_id)
        return list(db.scalars(query))

    def create(self, db: Session, values: dict[str, object]) -> Project:
        project = Project(**values)
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    def update(self, db: Session, project: Project, values: dict[str, object]) -> Project:
        for field, value in values.items():
            setattr(project, field, value)
        db.commit()
        db.refresh(project)
        return project

    def delete(self, db: Session, project: Project) -> None:
        db.delete(project)
        db.commit()


project_crud = ProjectCRUD()
