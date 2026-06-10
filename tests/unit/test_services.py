"""Service and utility tests."""

import pytest

from app.text_analysis.integration import TextAnalyzer
from app.security import hash_password, verify_password
from app.dto.project import ProjectCreate, ProjectUpdate
from app.dto.task import TaskCreate, TaskUpdate
from app.dto.user import UserCreate, UserUpdate
from app.services.analysis_service import TextAnalysisService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService
from app.services.user_service import UserService
from app.utils.exceptions import ConflictError, NotFoundError
from app.utils.rate_limit import SimpleRateLimiter
from app.utils.validators import ensure_text, normalize_tag_name


@pytest.mark.asyncio
async def test_user_service_create_conflict_and_update(db_session) -> None:
    service = UserService(db_session)
    user = await service.create_user(
        UserCreate(email="test@example.com", username="TestUser", password="secret123")
    )

    assert user.id > 0
    assert user.username == "testuser"
    assert verify_password("secret123", user.password_hash)

    with pytest.raises(ConflictError):
        await service.create_user(
            UserCreate(email="test@example.com", username="OtherUser", password="secret123")
        )

    updated = await service.update_user(user.id, UserUpdate(username="UpdatedUser"))
    assert updated.username == "updateduser"


@pytest.mark.asyncio
async def test_project_service_owner_and_duplicate_checks(db_session) -> None:
    project_service = ProjectService(db_session)

    with pytest.raises(NotFoundError):
        await project_service.create_project(ProjectCreate(owner_id=999, name="Missing Owner"))

    user = await UserService(db_session).create_user(
        UserCreate(email="owner@example.com", username="owner", password="secret123")
    )
    project = await project_service.create_project(ProjectCreate(owner_id=user.id, name="Platform"))

    with pytest.raises(ConflictError):
        await project_service.create_project(ProjectCreate(owner_id=user.id, name="Platform"))

    updated = await project_service.update_project(project.id, ProjectUpdate(status="completed"))
    assert updated.status == "completed"


@pytest.mark.asyncio
async def test_task_service_crud_and_summary(db_session) -> None:
    user = await UserService(db_session).create_user(
        UserCreate(email="task@example.com", username="tasker", password="secret123")
    )
    project = await ProjectService(db_session).create_project(
        ProjectCreate(owner_id=user.id, name="Backend")
    )
    service = TaskService(db_session)

    task = await service.create_task(
        TaskCreate(
            project_id=project.id,
            assignee_id=user.id,
            title="Critical API error",
            description="Urgent blocker creates error during checkout.",
            priority=4,
            tag_names=["Bug", "api"],
        )
    )
    assert task.tags[0].name == "bug"

    updated = await service.update_task(
        task.id,
        TaskUpdate(status="in_progress", tag_names=["bug", "critical"]),
    )
    assert updated.status == "in_progress"
    assert [tag.name for tag in updated.tags] == ["bug", "critical"]

    analysis = await service.analyze_task(task.id)
    assert analysis.sentiment == "negative"
    assert analysis.priority_score == 5

    await service.delete_task(task.id)
    with pytest.raises(NotFoundError):
        await service.get_task(task.id)


@pytest.mark.asyncio
async def test_task_service_missing_references(db_session) -> None:
    service = TaskService(db_session)
    with pytest.raises(NotFoundError):
        await service.create_task(TaskCreate(project_id=1, title="Missing project"))


@pytest.mark.asyncio
async def test_text_analysis_service_analyzes_text() -> None:
    result = await TextAnalysisService().analyze_text("Great progress, but urgent deadline risk.")
    assert result.sentiment == "neutral"
    assert result.priority_score >= 4
    assert "urgent" in result.keywords


@pytest.mark.asyncio
async def test_text_analyzer_rejects_blank_text() -> None:
    with pytest.raises(Exception):
        await TextAnalyzer().analyze_text("   ")


def test_password_verify_rejects_invalid_hash() -> None:
    assert verify_password("secret123", hash_password("secret123"))
    assert not verify_password("secret123", "bad-hash")


def test_validators() -> None:
    assert normalize_tag_name("API Work") == "api-work"
    assert ensure_text(" value ", "field") == "value"
    with pytest.raises(Exception):
        ensure_text(" ", "field")


def test_rate_limiter_window() -> None:
    limiter = SimpleRateLimiter(max_requests=2, window_seconds=10)
    assert limiter.allow("client", now=100)
    assert limiter.allow("client", now=101)
    assert not limiter.allow("client", now=102)
    assert limiter.allow("client", now=111)
