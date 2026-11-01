"""Dependências compartilhadas pelos routers. Tudo entra via `Depends`."""

from functools import lru_cache
from typing import Annotated, Protocol

import structlog
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import EmbeddingProvider, build_embedding_provider
from app.core.config import Settings, get_settings
from app.core.errors import UnauthorizedError
from app.db.session import get_session
from app.models.user import User
from app.services.auth import AuthService
from app.services.jobs import JobService
from app.services.resumes import ResumeService
from app.worker.queue import CeleryTaskQueue, TaskQueue


class PingableCache(Protocol):
    async def ping(self) -> bool: ...


def get_cache(request: Request) -> PingableCache:
    cache: PingableCache = request.app.state.redis
    return cache


SessionDep = Annotated[AsyncSession, Depends(get_session)]
CacheDep = Annotated[PingableCache, Depends(get_cache)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_auth_service(session: SessionDep, settings: SettingsDep) -> AuthService:
    return AuthService(session, settings)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

_bearer = HTTPBearer(auto_error=False, description="Access token devolvido por login/refresh.")


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    service: AuthServiceDep,
) -> User:
    """Usuário autenticado. Toda rota fora da lista pública depende disto."""
    if credentials is None:
        raise UnauthorizedError("Autenticação necessária.", code="not_authenticated")
    user = await service.authenticate(credentials.credentials)
    structlog.contextvars.bind_contextvars(user_id=str(user.id))
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Um cliente por processo (reaproveita conexões HTTP). Testes sobrescrevem via override."""
    return build_embedding_provider(get_settings())


EmbeddingDep = Annotated[EmbeddingProvider, Depends(get_embedding_provider)]


def get_resume_service(
    session: SessionDep, user: CurrentUserDep, settings: SettingsDep, embeddings: EmbeddingDep
) -> ResumeService:
    return ResumeService(session, user.id, settings, embeddings)


ResumeServiceDep = Annotated[ResumeService, Depends(get_resume_service)]


def get_task_queue() -> TaskQueue:
    """Fila do Celery. Testes sobrescrevem com `InMemoryTaskQueue` (o CI não tem Redis)."""
    return CeleryTaskQueue()


QueueDep = Annotated[TaskQueue, Depends(get_task_queue)]


def get_job_service(session: SessionDep, user: CurrentUserDep, queue: QueueDep) -> JobService:
    return JobService(session, user.id, queue)


JobServiceDep = Annotated[JobService, Depends(get_job_service)]
