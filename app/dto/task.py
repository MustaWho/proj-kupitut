"""Task and tag request/response schemas."""

from datetime import date, datetime
from typing import Literal

from pydantic import Field, field_validator

from app.dto.base import ORMBaseModel
from app.utils.exceptions import BadRequestError
from app.utils.validators import normalize_tag_name


TaskStatus = Literal["todo", "in_progress", "done", "cancelled"]


class TagRead(ORMBaseModel):
    """Tag response."""

    id: int
    name: str


class TaskBase(ORMBaseModel):
    """Shared task fields."""

    title: str = Field(min_length=3, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus = "todo"
    priority: int = Field(default=3, ge=1, le=5)
    due_date: date | None = None
    assignee_id: int | None = Field(default=None, gt=0)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str) -> str:
        """Remove leading and trailing whitespace from task titles."""

        return value.strip()


class TaskCreate(TaskBase):
    """Create task payload."""

    project_id: int = Field(gt=0)
    tag_names: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("tag_names")
    @classmethod
    def normalize_tags(cls, values: list[str]) -> list[str]:
        """Normalize tags and remove duplicates while preserving order."""

        normalized: list[str] = []
        for value in values:
            try:
                tag = normalize_tag_name(value)
            except BadRequestError as exc:
                raise ValueError(exc.message) from exc
            if tag not in normalized:
                normalized.append(tag)
        return normalized


class TaskUpdate(ORMBaseModel):
    """Update task payload."""

    title: str | None = Field(default=None, min_length=3, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    status: TaskStatus | None = None
    priority: int | None = Field(default=None, ge=1, le=5)
    due_date: date | None = None
    assignee_id: int | None = Field(default=None, gt=0)
    project_id: int | None = Field(default=None, gt=0)
    tag_names: list[str] | None = Field(default=None, max_length=10)

    @field_validator("title")
    @classmethod
    def strip_title(cls, value: str | None) -> str | None:
        """Remove leading and trailing whitespace from task titles."""

        return None if value is None else value.strip()

    @field_validator("tag_names")
    @classmethod
    def normalize_tags(cls, values: list[str] | None) -> list[str] | None:
        """Normalize tags and remove duplicates while preserving order."""

        if values is None:
            return None
        normalized: list[str] = []
        for value in values:
            try:
                tag = normalize_tag_name(value)
            except BadRequestError as exc:
                raise ValueError(exc.message) from exc
            if tag not in normalized:
                normalized.append(tag)
        return normalized


class TaskRead(TaskBase):
    """Task response."""

    id: int
    project_id: int
    analysis_summary: str | None
    tags: list[TagRead] = []
    created_at: datetime
    updated_at: datetime
