from typing import Any

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import FakeEmbeddingProvider
from app.ai.errors import AIProviderError
from app.ai.fake_llm import FakeLLMProvider
from app.ai.llm import LLMRequest
from app.core.config import get_settings
from app.models.application import Application
from app.models.user import User
from app.seed import DEMO_EMAIL, RESUME_TEXT, SeedRefusedError, SeedReport, seed

pytestmark = pytest.mark.integration


async def _run(session: AsyncSession, *, reset: bool = False) -> SeedReport:
    return await seed(
        session, get_settings(), FakeLLMProvider(), FakeEmbeddingProvider(), reset=reset
    )


async def _demo_users(session: AsyncSession) -> int:
    return await session.scalar(select(func.count()).where(User.email == DEMO_EMAIL)) or 0


async def test_seed_runs_the_whole_flow_with_fake_providers(db_session: AsyncSession) -> None:
    report = await _run(db_session)

    assert report.created is True
    assert [status for _, status, _ in report.analyses] == ["done", "done"]
    assert all(score is not None for _, _, score in report.analyses)
    assert report.screening_needs_input >= 1, "Kubernetes não está no currículo fictício"
    assert await db_session.scalar(select(func.count()).select_from(Application)) == 1


async def test_seed_survives_ai_outage(db_session: AsyncSession) -> None:
    def unavailable(_request: LLMRequest) -> dict[str, Any]:
        raise AIProviderError()

    llm = FakeLLMProvider(
        handlers={"extract_requirements": unavailable, "analyze_fit": unavailable}
    )

    report = await seed(db_session, get_settings(), llm, FakeEmbeddingProvider())

    assert report.created is True
    assert [status for _, status, _ in report.analyses] == ["failed", "failed"]
    assert all(title for title, _, _ in report.analyses)


async def test_seed_is_idempotent_and_reset_recreates(db_session: AsyncSession) -> None:
    await _run(db_session)

    again = await _run(db_session)
    reset = await _run(db_session, reset=True)

    assert again.created is False
    assert reset.created is True
    assert await _demo_users(db_session) == 1


async def test_seed_refuses_production(db_session: AsyncSession) -> None:
    settings = get_settings().model_copy(update={"environment": "production"})

    with pytest.raises(SeedRefusedError):
        await seed(db_session, settings, FakeLLMProvider(), FakeEmbeddingProvider())


def test_seed_data_is_marked_as_fictitious() -> None:
    assert "fictício" in RESUME_TEXT
    assert DEMO_EMAIL.endswith(".example")
