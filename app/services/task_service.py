"""Task business logic."""

from sqlalchemy.orm import Session

from app.repositories.project import project_crud
from app.repositories.task import task_crud
from app.repositories.user import user_crud
from app.models import Task
from app.dto.analysis import TextAnalysisRead
from app.dto.task import TaskCreate, TaskUpdate
from app.services.analysis_service import TextAnalysisService
from app.utils.exceptions import NotFoundError


class TaskService:
    """Use cases for tasks."""

    def __init__(self, db: Session, analysis_service: TextAnalysisService | None = None):
        self.db = db
        self.analysis_service = analysis_service or TextAnalysisService()

    async def create_task(self, payload: TaskCreate) -> Task:
        self._ensure_project(payload.project_id)
        self._ensure_assignee(payload.assignee_id)
        values = payload.model_dump(exclude={"tag_names"})
        tags = task_crud.get_or_create_tags(self.db, payload.tag_names)
        return task_crud.create(self.db, values, tags)

    async def list_tasks(
        self,
        project_id: int | None = None,
        status: str | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Task]:
        if project_id is not None:
            self._ensure_project(project_id)
        return task_crud.list_tasks(
            self.db,
            project_id=project_id,
            status=status,
            offset=offset,
            limit=limit,
        )

    async def get_task(self, task_id: int) -> Task:
        task = task_crud.get(self.db, task_id)
        if task is None:
            raise NotFoundError("Задача не найдена")
        return task

    async def update_task(self, task_id: int, payload: TaskUpdate) -> Task:
        task = await self.get_task(task_id)
        values = payload.model_dump(exclude_unset=True, exclude={"tag_names"})

        if "project_id" in values:
            self._ensure_project(int(values["project_id"]))
        if "assignee_id" in values:
            self._ensure_assignee(values["assignee_id"])

        tags = None
        if payload.tag_names is not None:
            tags = task_crud.get_or_create_tags(self.db, payload.tag_names)
        return task_crud.update(self.db, task, values, tags)

    async def delete_task(self, task_id: int) -> None:
        task = await self.get_task(task_id)
        task_crud.delete(self.db, task)

    async def analyze_task(self, task_id: int) -> TextAnalysisRead:
        task = await self.get_task(task_id)
        text = f"{task.title}. {task.description or ''}"
        analysis = await self.analysis_service.analyze_text(text)
        task.analysis_summary = analysis.summary
        self.db.commit()
        self.db.refresh(task)
        return analysis

    def _ensure_project(self, project_id: int) -> None:
        if project_crud.get(self.db, project_id) is None:
            raise NotFoundError("Проект не найден")

    def _ensure_assignee(self, assignee_id: int | None) -> None:
        if assignee_id is not None and user_crud.get(self.db, assignee_id) is None:
            raise NotFoundError("Исполнитель не найден")
