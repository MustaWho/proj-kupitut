"""FastAPI application entrypoint."""

import logging
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.controllers import health
from app.controllers.router import api_router
from app.utils.exceptions import register_exception_handlers
from app.utils.rate_limit import SimpleRateLimiter


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    logging.basicConfig(level=settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    limiter = SimpleRateLimiter(
        max_requests=settings.rate_limit_requests,
        window_seconds=settings.rate_limit_window_seconds,
    )
    cors_origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):  # type: ignore[no-untyped-def]
        if request.url.path.startswith("/api/"):
            client_host = request.client.host if request.client else "unknown"
            if not limiter.allow(client_host):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": {
                            "code": "rate_limited",
                            "message": "Слишком много запросов",
                        }
                    },
                )
        return await call_next(request)

    register_exception_handlers(app)
    media_root = Path(settings.media_dir)
    media_root.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=media_root), name="media")
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(health.router, prefix="/api")

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"message": settings.app_name, "docs": "/docs"}

    return app


app = create_app()
