"""Schema validation tests."""

import pytest
from pydantic import ValidationError

from app.dto.analysis import TextAnalysisRequest
from app.dto.project import ProjectCreate
from app.dto.task import TaskCreate, TaskUpdate
from app.dto.user import UserCreate, UserUpdate


def test_user_create_normalizes_username() -> None:
    schema = UserCreate(email="Test@Example.com", username="User_One", password="secret123")
    assert schema.username == "user_one"


def test_user_create_rejects_bad_email() -> None:
    with pytest.raises(ValidationError):
        UserCreate(email="bad", username="User_One", password="secret123")


def test_user_update_password_length() -> None:
    with pytest.raises(ValidationError):
        UserUpdate(password="short")


def test_project_create_strips_name() -> None:
    schema = ProjectCreate(owner_id=1, name="  API Project  ", status="planned")
    assert schema.name == "API Project"


def test_task_create_normalizes_and_deduplicates_tags() -> None:
    schema = TaskCreate(
        project_id=1,
        title="Fix API",
        tag_names=["Backend", "backend", "api work"],
    )
    assert schema.tag_names == ["backend", "api-work"]


def test_task_create_rejects_bad_priority() -> None:
    with pytest.raises(ValidationError):
        TaskCreate(project_id=1, title="Fix API", priority=8)


def test_task_create_rejects_bad_tag() -> None:
    with pytest.raises(ValidationError):
        TaskCreate(project_id=1, title="Fix API", tag_names=["!"])


def test_task_update_allows_empty_tag_list() -> None:
    schema = TaskUpdate(tag_names=[])
    assert schema.tag_names == []


def test_text_analysis_request_requires_text() -> None:
    with pytest.raises(ValidationError):
        TextAnalysisRequest(text="no")
