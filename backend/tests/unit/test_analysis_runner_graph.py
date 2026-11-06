"""`AnalysisRunner` com o grafo, sem banco: repositórios e etapas de dados são stubs.

Garante que as exceções do grafo chegam ao runner sem embrulho e viram o status e a mensagem
certos. A cobertura com banco de verdade fica em `tests/integration/test_analyses.py`.
"""

import uuid
from typing import Any

import pytest

from app.ai.embeddings import FakeEmbeddingProvider
from app.ai.errors import AIProviderError, AIQuotaExceededError
from app.ai.fake_llm import FakeLLMProvider
from app.ai.llm import LLMRequest
from app.core.config import Settings
from app.models.analysis import Analysis
from app.models.resume import ResumeChunk
from app.schemas.extraction import JobExtraction
from app.services import analysis as analysis_module
from app.services.analysis import (
    MSG_AI_QUOTA,
    MSG_AI_UNAVAILABLE,
    MSG_INVALID_OUTPUT,
    MSG_MISSING_INPUT,
    AnalysisRunner,
)
from app.services.retrieval import RetrievedContext
from tests.unit.test_analysis_graph import CHUNK, EXTRACTION, INVALID, VALID


class _Session:
    commits = 0

    async def commit(self) -> None:
        self.commits += 1

    async def rollback(self) -> None:
        return None


class _AnalysisRepo:
    store: dict[uuid.UUID, Analysis] = {}  # noqa: RUF012

    def __init__(self, *_: Any) -> None:
        return None

    async def get(self, analysis_id: uuid.UUID) -> Analysis | None:
        return self.store.get(analysis_id)


class _ResumeRepo:
    def __init__(self, *_: Any) -> None:
        return None

    async def get(self, resume_id: uuid.UUID) -> object:
        return object()


class _RaisingLLM:
    model = "fake-llm"

    def __init__(self, error: Exception) -> None:
        self._error = error

    async def complete_json(self, request: LLMRequest) -> str:
        raise self._error

    async def aclose(self) -> None:
        return None


@pytest.fixture
def analysis(monkeypatch: pytest.MonkeyPatch) -> Analysis:
    item = Analysis(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        resume_id=uuid.uuid4(),
        job_id=uuid.uuid4(),
        status="pending",
        input_hash="h",
    )
    _AnalysisRepo.store = {item.id: item}
    chunk = ResumeChunk(
        id=uuid.uuid4(),
        content=CHUNK,
        ordinal=0,
    )
    ctx = RetrievedContext(chunks={"C1": chunk}, candidates={"R1": ["C1"], "R2": ["C1"]})

    async def fake_extract(*_: Any) -> JobExtraction | None:
        return EXTRACTION

    async def fake_retrieve(*_: Any) -> RetrievedContext:
        return ctx

    monkeypatch.setattr(analysis_module, "AnalysisRepository", _AnalysisRepo)
    monkeypatch.setattr(analysis_module, "ResumeRepository", _ResumeRepo)
    monkeypatch.setattr(analysis_module, "ensure_extracted", fake_extract)
    monkeypatch.setattr(analysis_module, "retrieve", fake_retrieve)
    return item


def _runner(llm: Any) -> AnalysisRunner:
    return AnalysisRunner(
        _Session(),  # type: ignore[arg-type]
        uuid.uuid4(),
        Settings(_env_file=None),
        llm,
        FakeEmbeddingProvider(),
    )


async def test_done_stores_score_and_result(analysis: Analysis) -> None:
    status = await _runner(FakeLLMProvider(scripted=[VALID])).run(analysis.id)

    assert status == "done"
    assert analysis.status == "done"
    assert analysis.score == 70
    assert analysis.result is not None
    assert analysis.error is None


async def test_one_invalid_answer_is_retried_and_still_done(analysis: Analysis) -> None:
    llm = FakeLLMProvider(scripted=[INVALID, VALID])

    assert await _runner(llm).run(analysis.id) == "done"
    assert len(llm.requests) == 2


async def test_two_invalid_answers_fail_with_clear_message(analysis: Analysis) -> None:
    assert await _runner(FakeLLMProvider(scripted=[INVALID, INVALID])).run(analysis.id) == "failed"
    assert analysis.status == "failed"
    assert analysis.error == MSG_INVALID_OUTPUT


@pytest.mark.parametrize(
    ("error", "message"),
    [
        (AIProviderError(), MSG_AI_UNAVAILABLE),
        (AIQuotaExceededError(), MSG_AI_QUOTA),
    ],
)
async def test_provider_errors_pass_through_the_graph_unchanged(
    analysis: Analysis, error: Exception, message: str
) -> None:
    assert await _runner(_RaisingLLM(error)).run(analysis.id) == "failed"
    assert analysis.error == message


async def test_missing_job_fails_with_missing_input(
    analysis: Analysis, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def gone(*_: Any) -> None:
        return None

    monkeypatch.setattr(analysis_module, "ensure_extracted", gone)

    assert await _runner(FakeLLMProvider()).run(analysis.id) == "failed"
    assert analysis.error == MSG_MISSING_INPUT


async def test_unknown_or_finished_analysis_is_not_rerun(analysis: Analysis) -> None:
    analysis.status = "done"
    llm = FakeLLMProvider(scripted=[VALID])

    assert await _runner(llm).run(analysis.id) == "done"
    assert await _runner(llm).run(uuid.uuid4()) is None
    assert llm.requests == []
