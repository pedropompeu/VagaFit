import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.worker.runtime import run_async

pytestmark = pytest.mark.integration


def test_pgvector_extension_is_installed() -> None:
    async def job(session: AsyncSession) -> str | None:
        result = await session.execute(
            text("SELECT extversion FROM pg_extension WHERE extname = 'vector'")
        )
        return result.scalar_one_or_none()

    assert run_async(job, database_url=get_settings().database_url) is not None
