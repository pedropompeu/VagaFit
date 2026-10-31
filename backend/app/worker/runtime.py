"""Ponte entre task Celery (síncrona) e o código async (services e repositories).

Decisão [2026-10-31] (d): cada task roda em `asyncio.run()` com um engine próprio em
NullPool. Reaproveitar o engine da API dentro do worker prende conexões asyncpg a um
loop de eventos que já foi fechado, e a falha aparece de forma intermitente.
"""

import asyncio
from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import build_engine, build_sessionmaker


def run_async[T](
    job: Callable[[AsyncSession], Awaitable[T]],
    *,
    database_url: str | None = None,
) -> T:
    """Executa `job(session)` num loop novo, com engine descartado ao final."""

    async def _runner() -> T:
        engine = build_engine(database_url or get_settings().database_url, null_pool=True)
        try:
            async with build_sessionmaker(engine)() as session:
                return await job(session)
        finally:
            await engine.dispose()

    return asyncio.run(_runner())
