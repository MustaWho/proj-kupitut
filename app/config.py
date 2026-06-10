"""Application settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "Интернет-магазин API"
    app_version: str = "0.1.0"
    environment: Literal["local", "test", "production"] = "local"
    debug: bool = True
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://projr:projr@localhost:5432/projr"
    test_database_url: str = "sqlite+pysqlite:///:memory:"
    rate_limit_requests: int = Field(default=100, ge=1)
    rate_limit_window_seconds: int = Field(default=60, ge=1)
    log_level: str = "INFO"
    token_secret: str = "dev-shop-secret"
    access_token_seconds: int = Field(default=3600, ge=60)
    refresh_token_seconds: int = Field(default=604800, ge=3600)
    cors_origins: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"
    media_dir: str = "media"


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()


settings = get_settings()
