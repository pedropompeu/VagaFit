"""Ponto de entrada da API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis.asyncio import Redis
from slowapi.errors import RateLimitExceeded

from app import __version__
from app.api.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import ErrorResponse, register_exception_handlers
from app.core.logging import REQUEST_ID_HEADER, RequestIdMiddleware, configure_logging
from app.core.metrics import instrument
from app.core.rate_limit import limiter, rate_limit_exceeded_handler
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.redis = Redis.from_url(get_settings().redis_url)
    try:
        yield
    finally:
        await app.state.redis.aclose()
        await engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    app = FastAPI(
        title="VagaFit API",
        version=__version__,
        description=(
            "Compara uma vaga com o currículo do usuário e devolve aderência por requisito, "
            "sempre com evidência citada do próprio currículo."
        ),
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
        docs_url="/docs",
        redoc_url=None,
        lifespan=lifespan,
        responses={500: {"model": ErrorResponse, "description": "Erro interno"}},
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type", REQUEST_ID_HEADER],
        expose_headers=[REQUEST_ID_HEADER],
    )
    app.add_middleware(RequestIdMiddleware)
    register_exception_handlers(app)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    app.include_router(health_router)
    instrument(app)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
