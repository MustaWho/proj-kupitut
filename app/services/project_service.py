"""Project business logic."""

from sqlalchemy.orm import Session

from app.repositories.project import project_crud
from app.repositories.user import user_crud
from app.models import Project
from app.dto.project import ProjectCreate, ProjectUpdate
from app.utils.exceptions import ConflictError, NotFoundError


class ProjectService:
    """Use cases for projects."""

    def __init__(self, db: Session):
        self.db = db

    async def create_project(self, payload: ProjectCreate) -> Project:
        if user_crud.get(self.db, payload.owner_id) is None:
            raise NotFoundError("Владелец проекта не найден")
        if project_crud.get_by_owner_and_name(self.db, payload.owner_id, payload.name):
            raise ConflictError("У этого владельца уже есть проект с таким названием")
        return project_crud.create(self.db, payload.model_dump())

    async def list_projects(
        self,
        owner_id: int | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Project]:
        return project_crud.list(self.db, owner_id=owner_id, offset=offset, limit=limit)

    async def get_project(self, project_id: int) -> Project:
        project = project_crud.get(self.db, project_id)
        if project is None:
            raise NotFoundError("Проект не найден")
        return project

    async def update_project(self, project_id: int, payload: ProjectUpdate) -> Project:
        project = await self.get_project(project_id)
        values = payload.model_dump(exclude_unset=True)
        if "name" in values:
            existing = project_crud.get_by_owner_and_name(self.db, project.owner_id, values["name"])
            if existing and existing.id != project_id:
                raise ConflictError("У этого владельца уже есть проект с таким названием")
        return project_crud.update(self.db, project, values)

    async def delete_project(self, project_id: int) -> None:
        project = await self.get_project(project_id)
        project_crud.delete(self.db, project)
