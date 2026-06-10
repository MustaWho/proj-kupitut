"""Health endpoint."""

from fastapi import APIRouter

from app.config import settings
from app.dto.health import HealthRead

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthRead)
async def health_check() -> HealthRead:
    """Return application health information."""

    return HealthRead(
        status="ok",
        app=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
