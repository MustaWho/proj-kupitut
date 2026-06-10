"""Database integration tests."""

from sqlalchemy import select

from app.models import Project, Tag, Task, User
from app.dto.project import ProjectCreate
from app.dto.task import TaskCreate
from app.dto.user import UserCreate
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.user_service import UserService


async def create_graph(db_session):
    user = await UserService(db_session).create_user(
        UserCreate(email="db@example.com", username="dbuser", password="secret123")
    )
    project = await ProjectService(db_session).create_project(
        ProjectCreate(owner_id=user.id, name="Database")
    )
    task = await TaskService(db_session).create_task(
        TaskCreate(project_id=project.id, title="Check schema", tag_names=["database"])
    )
    return user, project, task


def test_tables_are_created(db_session) -> None:
    assert db_session.scalar(select(User).limit(1)) is None
    assert db_session.scalar(select(Project).limit(1)) is None
    assert db_session.scalar(select(Task).limit(1)) is None
    assert db_session.scalar(select(Tag).limit(1)) is None


async def test_relationships_are_persisted(db_session) -> None:
    user, project, task = await create_graph(db_session)

    db_session.refresh(user)
    db_session.refresh(project)
    db_session.refresh(task)

    assert project.owner_id == user.id
    assert task.project_id == project.id
    assert task.tags[0].name == "database"
