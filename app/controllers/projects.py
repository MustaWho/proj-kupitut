"""Project endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.controllers.dependencies import get_db
from app.models import Project
from app.dto.project import ProjectCreate, ProjectRead, ProjectUpdate
from app.services.project_service import ProjectService

router = APIRouter()


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Project:
    """Create a project."""

    return await ProjectService(db).create_project(payload)


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    db: Annotated[Session, Depends(get_db)],
    owner_id: Annotated[int | None, Query(gt=0)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
) -> list[Project]:
    """List projects."""

    return await ProjectService(db).list_projects(owner_id=owner_id, offset=offset, limit=limit)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: int, db: Annotated[Session, Depends(get_db)]) -> Project:
    """Get a project by id."""

    return await ProjectService(db).get_project(project_id)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> Project:
    """Update a project."""

    return await ProjectService(db).update_project(project_id, payload)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: int, db: Annotated[Session, Depends(get_db)]) -> Response:
    """Delete a project."""

    await ProjectService(db).delete_project(project_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
