"""Engine e sessões assíncronas.

A API usa um engine com pool, criado uma vez. O worker NÃO usa este engine: cada task
cria o seu com NullPool (ver `app.worker.runtime`).
"""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import get_settings


def build_engine(database_url: str, *, null_pool: bool = False) -> AsyncEngine:
    if null_pool:
        return create_async_engine(database_url, poolclass=NullPool)
    return create_async_engine(database_url, pool_pre_ping=True)


def build_sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


engine = build_engine(get_settings().database_url)
SessionLocal = build_sessionmaker(engine)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Dependência do FastAPI: uma sessão por requisição."""
    async with SessionLocal() as session:
        yield session
