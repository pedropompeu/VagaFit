"""Dependências compartilhadas pelos routers. Tudo entra via `Depends`."""

from typing import Annotated, Protocol

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session


class PingableCache(Protocol):
    async def ping(self) -> bool: ...


def get_cache(request: Request) -> PingableCache:
    cache: PingableCache = request.app.state.redis
    return cache


SessionDep = Annotated[AsyncSession, Depends(get_session)]
CacheDep = Annotated[PingableCache, Depends(get_cache)]
