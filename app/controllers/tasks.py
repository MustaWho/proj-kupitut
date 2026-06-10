"""Task endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers.dependencies import get_db
from app.models import Task
from app.dto.analysis import TextAnalysisRead
from app.dto.task import TaskCreate, TaskRead, TaskStatus, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter()


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, db: Annotated[Session, Depends(get_db)]) -> Task:
    """Create a task."""

    return await TaskService(db).create_task(payload)


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    db: Annotated[Session, Depends(get_db)],
    project_id: Annotated[int | None, Query(gt=0)] = None,
    task_status: Annotated[TaskStatus | None, Query(alias="status")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[Task]:
    """List tasks."""

    return await TaskService(db).list_tasks(
        project_id=project_id,
        status=task_status,
        offset=offset,
        limit=limit,
    )


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: int, db: Annotated[Session, Depends(get_db)]) -> Task:
    """Get a task by id."""

    return await TaskService(db).get_task(task_id)


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    payload: TaskUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Task:
    """Update a task."""

    return await TaskService(db).update_task(task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: Annotated[Session, Depends(get_db)]) -> Response:
    """Delete a task."""

    await TaskService(db).delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{task_id}/summary", response_model=TextAnalysisRead)
async def analyze_task(task_id: int, db: Annotated[Session, Depends(get_db)]) -> TextAnalysisRead:
    """Generate and store a text summary for a task."""

    return await TaskService(db).analyze_task(task_id)
