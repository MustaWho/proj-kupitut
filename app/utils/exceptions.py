"""Application exceptions and FastAPI handlers."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class AppError(Exception):
    """Base exception carrying an HTTP status code and machine-readable code."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "app_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(AppError):
    """Requested resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    code = "not_found"


class ConflictError(AppError):
    """Request conflicts with existing state."""

    status_code = status.HTTP_409_CONFLICT
    code = "conflict"


class BadRequestError(AppError):
    """Request is semantically invalid."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "bad_request"


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Build a consistent JSON error response."""

    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


async def app_error_handler(_: Request, exc: Exception) -> JSONResponse:
    """Handle known application errors."""

    if isinstance(exc, AppError):
        return error_response(exc.status_code, exc.code, exc.message)
    return error_response(status.HTTP_500_INTERNAL_SERVER_ERROR, "app_error", "Ошибка приложения")


async def sqlalchemy_error_handler(_: Request, __: Exception) -> JSONResponse:
    """Hide low-level database details from API consumers."""

    return error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "database_error",
        "Не удалось выполнить операцию с базой данных",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers on a FastAPI app."""

    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)
