import uuid
from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.errors import AIProviderError
from app.ai.fake_llm import FakeLLMProvider, screening
from app.ai.llm import LLMRequest
from app.api.deps import get_llm_provider
from app.repositories.resumes import ResumeRepository
from tests.integration.conftest import AuthedUser
from tests.integration.test_analyses import _request, _runner, _setup

pytestmark = pytest.mark.integration

QUESTIONS = ["Você tem experiência com FastAPI?", "Qual sua pretensão salarial?"]


@pytest.fixture
def use_llm(app: FastAPI) -> Iterator[list[FakeLLMProvider]]:
    """Troca o LLM da API: `use_llm.append(FakeLLMProvider(...))` antes da requisição."""
    holder: list[FakeLLMProvider] = [FakeLLMProvider()]
    app.dependency_overrides[get_llm_provider] = lambda: holder[-1]
    yield holder
    app.dependency_overrides.pop(get_llm_provider, None)


async def _done_analysis(
    client: AsyncClient, user: AuthedUser, session: AsyncSession
) -> tuple[str, str]:
    resume_id, job_id = await _setup(client, user)
    created = (await _request(client, user, resume_id, job_id)).json()
    assert await _runner(session, user, FakeLLMProvider()).run(uuid.UUID(created["id"])) == "done"
    return created["id"], resume_id


async def _screen(client: AsyncClient, user: AuthedUser, analysis_id: str, questions: list[str]):
    return await client.post(
        f"/api/v1/analyses/{analysis_id}/screening",
        json={"questions": questions},
        headers=user.headers,
    )


async def test_answers_with_evidence_or_asks_the_user(
    client: AsyncClient,
    user_a: AuthedUser,
    db_session: AsyncSession,
    use_llm: list[FakeLLMProvider],
) -> None:
    analysis_id, resume_id = await _done_analysis(client, user_a, db_session)

    response = await _screen(client, user_a, analysis_id, [f"  {QUESTIONS[0]} ", QUESTIONS[1]])

    assert response.status_code == 201, response.text
    grounded, missing = response.json()
    assert grounded["question"] == QUESTIONS[0]
    assert grounded["needs_user_input"] is False
    assert grounded["user_question"] is None
    assert "FastAPI" in grounded["answer"]
    assert grounded["evidence_chunk_ids"] == [grounded["evidence"][0]["chunk_id"]]

    resumes = ResumeRepository(db_session, user_a.id)
    resume = await resumes.get(uuid.UUID(resume_id), with_chunks=True)
    assert resume is not None
    contents = {str(c.id): c.content for c in resume.chunks}
    assert grounded["evidence"][0]["quote"] in contents[grounded["evidence"][0]["chunk_id"]]

    assert missing["needs_user_input"] is True
    assert missing["evidence"] == []
    assert missing["user_question"]

    # O prompt só leva trechos do currículo e as perguntas entre tags.
    sent = use_llm[-1].requests[-1]
    assert sent.task == "screening"
    assert "<perguntas>" in sent.user

    listing = await client.get(f"/api/v1/analyses/{analysis_id}/screening", headers=user_a.headers)
    assert [a["id"] for a in listing.json()] == [grounded["id"], missing["id"]]


async def test_requires_done_analysis(client: AsyncClient, user_a: AuthedUser) -> None:
    resume_id, job_id = await _setup(client, user_a)
    pending = (await _request(client, user_a, resume_id, job_id)).json()

    response = await _screen(client, user_a, pending["id"], QUESTIONS)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


async def test_invented_quote_twice_returns_502_and_saves_nothing(
    client: AsyncClient,
    user_a: AuthedUser,
    db_session: AsyncSession,
    use_llm: list[FakeLLMProvider],
) -> None:
    analysis_id, _ = await _done_analysis(client, user_a, db_session)

    def liar(request: LLMRequest) -> dict:
        output = screening(request)
        output["answers"][0]["evidence"][0]["quote"] = "Liderei a migração para FastAPI."
        return output

    use_llm.append(FakeLLMProvider(handlers={"screening": liar}))
    response = await _screen(client, user_a, analysis_id, QUESTIONS)

    assert response.status_code == 502
    assert response.json()["error"]["code"] == "ai_invalid_output"
    assert len(use_llm[-1].requests) == 2
    listing = await client.get(f"/api/v1/analyses/{analysis_id}/screening", headers=user_a.headers)
    assert listing.json() == []


async def test_ai_unavailable_is_503(
    client: AsyncClient,
    user_a: AuthedUser,
    db_session: AsyncSession,
    use_llm: list[FakeLLMProvider],
) -> None:
    analysis_id, _ = await _done_analysis(client, user_a, db_session)

    def down(request: LLMRequest) -> dict:
        raise AIProviderError

    use_llm.append(FakeLLMProvider(handlers={"screening": down}))
    response = await _screen(client, user_a, analysis_id, QUESTIONS)
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ai_unavailable"


@pytest.mark.parametrize(
    "questions", [[], ["ok?"] * 11, ["oi"], ["x" * 501]], ids=["empty", "11", "short", "long"]
)
async def test_validates_questions(
    client: AsyncClient, user_a: AuthedUser, questions: list[str]
) -> None:
    response = await _screen(client, user_a, str(uuid.uuid4()), questions)
    assert response.status_code == 422


async def test_isolation_between_users(
    client: AsyncClient, user_a: AuthedUser, user_b: AuthedUser, db_session: AsyncSession
) -> None:
    analysis_id, _ = await _done_analysis(client, user_a, db_session)
    assert (await _screen(client, user_a, analysis_id, QUESTIONS)).status_code == 201

    assert (await _screen(client, user_b, analysis_id, QUESTIONS)).status_code == 404
    listing = await client.get(f"/api/v1/analyses/{analysis_id}/screening", headers=user_b.headers)
    assert listing.status_code == 404
