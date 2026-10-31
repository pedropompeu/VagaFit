"""Health check: verifica banco e Redis. 200 se tudo responde, 503 se algo falha."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any, Literal

import structlog
from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from app.api.deps import CacheDep, SessionDep
from app.core.config import get_settings

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["health"])

CheckStatus = Literal["ok", "error"]


class HealthResponse(BaseModel):
    status: CheckStatus = Field(examples=["ok"])
    checks: dict[str, CheckStatus] = Field(examples=[{"database": "ok", "redis": "ok"}])


async def _probe(name: str, call: Callable[[], Awaitable[Any]]) -> CheckStatus:
    try:
        await asyncio.wait_for(call(), timeout=get_settings().health_check_timeout_seconds)
    except Exception as exc:
        logger.warning("health_check_failed", check=name, error_type=type(exc).__name__)
        return "error"
    return "ok"


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Estado da API e das dependências",
    responses={503: {"model": HealthResponse, "description": "Alguma dependência falhou"}},
)
async def health(response: Response, session: SessionDep, cache: CacheDep) -> HealthResponse:
    checks: dict[str, CheckStatus] = {
        "database": await _probe("database", lambda: session.execute(text("SELECT 1"))),
        "redis": await _probe("redis", cache.ping),
    }
    healthy = all(value == "ok" for value in checks.values())
    if not healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return HealthResponse(status="ok" if healthy else "error", checks=checks)
