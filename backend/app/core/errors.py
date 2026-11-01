"""Erros padronizados: toda resposta de erro tem o formato
`{"error": {"code": "...", "message": "..."}}`.
"""

from collections.abc import Mapping
from http import HTTPStatus
from types import MappingProxyType
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger(__name__)


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[dict[str, Any]] | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


class AppError(Exception):
    """Erro de domínio. Services levantam; o handler converte em resposta HTTP."""

    status_code: int = HTTPStatus.BAD_REQUEST
    code: str = "bad_request"

    headers: Mapping[str, str] | None = None

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        status_code: int | None = None,
        headers: Mapping[str, str] | None = None,
    ):
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        if status_code is not None:
            self.status_code = status_code
        if headers is not None:
            self.headers = headers


class NotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND
    code = "not_found"


class UnauthorizedError(AppError):
    status_code = HTTPStatus.UNAUTHORIZED
    code = "unauthorized"
    headers = MappingProxyType({"WWW-Authenticate": "Bearer"})


class ForbiddenError(AppError):
    status_code = HTTPStatus.FORBIDDEN
    code = "forbidden"


class ConflictError(AppError):
    status_code = HTTPStatus.CONFLICT
    code = "conflict"


def error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[dict[str, Any]] | None = None,
    headers: Mapping[str, str] | None = None,
) -> JSONResponse:
    body = ErrorResponse(error=ErrorBody(code=code, message=message, details=details))
    return JSONResponse(
        status_code=status_code,
        content=body.model_dump(exclude_none=True),
        headers=headers,
    )


_HTTP_CODES: dict[int, str] = {
    HTTPStatus.BAD_REQUEST: "bad_request",
    HTTPStatus.UNAUTHORIZED: "unauthorized",
    HTTPStatus.FORBIDDEN: "forbidden",
    HTTPStatus.NOT_FOUND: "not_found",
    HTTPStatus.METHOD_NOT_ALLOWED: "method_not_allowed",
    HTTPStatus.CONFLICT: "conflict",
    HTTPStatus.REQUEST_ENTITY_TOO_LARGE: "payload_too_large",
    HTTPStatus.UNSUPPORTED_MEDIA_TYPE: "unsupported_media_type",
    HTTPStatus.TOO_MANY_REQUESTS: "rate_limited",
}


async def app_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, AppError)  # noqa: S101 - garantido pelo registro do handler
    return error_response(exc.status_code, exc.code, exc.message, headers=exc.headers)


async def http_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, StarletteHTTPException)  # noqa: S101
    code = _HTTP_CODES.get(exc.status_code, "http_error")
    message = exc.detail if isinstance(exc.detail, str) else HTTPStatus(exc.status_code).phrase
    return error_response(exc.status_code, code, message, headers=exc.headers)


async def validation_error_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RequestValidationError)  # noqa: S101
    details = [
        {"loc": list(err.get("loc", ())), "msg": err.get("msg", ""), "type": err.get("type", "")}
        for err in exc.errors()
    ]
    return error_response(
        HTTPStatus.UNPROCESSABLE_ENTITY,
        "validation_error",
        "Dados de entrada inválidos.",
        details=details,
    )


async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_error", error_type=type(exc).__name__)
    return error_response(
        HTTPStatus.INTERNAL_SERVER_ERROR, "internal_error", "Erro interno inesperado."
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_error_handler)
