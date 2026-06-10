"""Shared Pydantic schema configuration."""

from pydantic import BaseModel, ConfigDict


class ORMBaseModel(BaseModel):
    """Base schema that can serialize SQLAlchemy objects."""

    model_config = ConfigDict(from_attributes=True)
