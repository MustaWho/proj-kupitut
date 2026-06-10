"""Project request and response schemas."""

from datetime import datetime
from typing import Literal

from pydantic import Field, field_validator

from app.dto.base import ORMBaseModel


ProjectStatus = Literal["planned", "active", "completed", "archived"]


class ProjectBase(ORMBaseModel):
    """Shared project fields."""

    name: str = Field(min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    status: ProjectStatus = "active"

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        """Remove leading and trailing whitespace from project names."""

        return value.strip()


class ProjectCreate(ProjectBase):
    """Create project payload."""

    owner_id: int = Field(gt=0)


class ProjectUpdate(ORMBaseModel):
    """Update project payload."""

    name: str | None = Field(default=None, min_length=3, max_length=120)
    description: str | None = Field(default=None, max_length=1000)
    status: ProjectStatus | None = None

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str | None) -> str | None:
        """Remove leading and trailing whitespace from project names."""

        return None if value is None else value.strip()


class ProjectRead(ProjectBase):
    """Project response."""

    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
