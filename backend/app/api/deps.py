"""Dependências compartilhadas pelos routers. Tudo entra via `Depends`."""

from typing import Annotated, Protocol

import structlog
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import UnauthorizedError
from app.db.session import get_session
from app.models.user import User
from app.services.auth import AuthService


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
