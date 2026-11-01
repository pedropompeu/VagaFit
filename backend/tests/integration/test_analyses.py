import uuid
from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import FakeEmbeddingProvider
from app.ai.errors import AIProviderError
from app.ai.fake_llm import FakeLLMProvider, analyze_fit
from app.ai.llm import LLMRequest
from app.core.config import get_settings
from app.models.mixins import utcnow
from app.repositories.analyses import AnalysisRepository
from app.repositories.resumes import ResumeRepository
from app.services.analysis import (
    MSG_AI_UNAVAILABLE,
    MSG_INTERNAL,
    MSG_INVALID_OUTPUT,
    AnalysisRunner,
)
from app.worker.queue import RUN_ANALYSIS_TASK, InMemoryTaskQueue
from tests.integration.conftest import AuthedUser

pytestmark = pytest.mark.integration

RESUME_TEXT = """RESUMO
Desenvolvedora backend com foco em Python.

EXPERIÊNCIA
Desenvolvedora Backend, Acme Ltda, 2021-2024
- Criei APIs REST em FastAPI.
- Usei PostgreSQL em produção.

FORMAÇÃO
Ciência da Computação, Universidade Exemplo, 2017
"""

JOB_TEXT = """Desenvolvedora Backend Pleno

Requisitos
- Python
- PostgreSQL
- Kubernetes

Diferenciais
- FastAPI
"""


async def _setup(client: AsyncClient, user: AuthedUser) -> tuple[str, str]:
    resume = await client.post(
        "/api/v1/resumes", data={"title": "CV", "text": RESUME_TEXT}, headers=user.headers
    )
    job = await client.post("/api/v1/jobs", json={"raw_text": JOB_TEXT}, headers=user.headers)
    assert resume.status_code == 201, resume.text
    assert job.status_code == 201, job.text
    return resume.json()["id"], job.json()["id"]


async def _request(client: AsyncClient, user: AuthedUser, resume_id: str, job_id: str):
    return await client.post(
        "/api/v1/analyses",
        json={"resume_id": resume_id, "job_id": job_id},
        headers=user.headers,
    )


def _runner(session: AsyncSession, user: AuthedUser, llm: FakeLLMProvider) -> AnalysisRunner:
    return AnalysisRunner(session, user.id, get_settings(), llm, FakeEmbeddingProvider())


async def test_request_enqueues_and_is_pending(
    client: AsyncClient, user_a: AuthedUser, task_queue: InMemoryTaskQueue
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    response = await _request(client, user_a, resume_id, job_id)

    assert response.status_code == 202, response.text
    body = response.json()
    assert body["status"] == "pending"
    assert body["reused"] is False
    assert body["score"] is None
    assert task_queue.sent[-1] == (RUN_ANALYSIS_TASK, (body["id"], str(user_a.id)))

    detail = await client.get(f"/api/v1/analyses/{body['id']}", headers=user_a.headers)
    assert detail.json()["result"] is None


async def test_runner_produces_literal_evidence_from_this_resume(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    created = (await _request(client, user_a, resume_id, job_id)).json()

    status = await _runner(db_session, user_a, FakeLLMProvider()).run(uuid.UUID(created["id"]))
    assert status == "done"

    detail = (await client.get(f"/api/v1/analyses/{created['id']}", headers=user_a.headers)).json()
    assert detail["status"] == "done"
    assert detail["finished_at"] is not None
    result = detail["result"]
    verdicts = {r["text"]: r["verdict"] for r in result["requirements"]}
    assert verdicts == {
        "Python": "met",
        "PostgreSQL": "met",
        "Kubernetes": "not_met",
        "FastAPI": "met",
    }
    # 0.7 * 2/3 + 0.3 * 1 = 0.7667
    assert detail["score"] == result["score"] == 77
    assert [g["text"] for g in result["gaps"]] == ["Kubernetes"]

    resume = await ResumeRepository(db_session, user_a.id).get(uuid.UUID(resume_id))
    assert resume is not None
    contents = {c.id: c.content for c in resume.chunks}
    for req in result["requirements"]:
        for ev in req["evidence"]:
            assert ev["quote"] in contents[uuid.UUID(ev["chunk_id"])]
    for s in result["suggestions"]:
        assert s["original"] in contents[uuid.UUID(s["chunk_id"])]


async def test_same_input_reuses_done_analysis(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession, task_queue: InMemoryTaskQueue
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    first = (await _request(client, user_a, resume_id, job_id)).json()
    await _runner(db_session, user_a, FakeLLMProvider()).run(uuid.UUID(first["id"]))
    sent_before = len(task_queue.sent)

    again = (await _request(client, user_a, resume_id, job_id)).json()

    assert again["id"] == first["id"]
    assert again["reused"] is True
    assert again["status"] == "done"
    assert len(task_queue.sent) == sent_before


async def test_pending_is_reused_until_stale(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    first = (await _request(client, user_a, resume_id, job_id)).json()
    assert (await _request(client, user_a, resume_id, job_id)).json()["id"] == first["id"]

    analysis = await AnalysisRepository(db_session, user_a.id).get(uuid.UUID(first["id"]))
    assert analysis is not None
    analysis.created_at = utcnow() - timedelta(hours=1)
    await db_session.commit()

    again = (await _request(client, user_a, resume_id, job_id)).json()
    assert again["id"] != first["id"]
    assert again["reused"] is False


async def test_failed_analysis_is_not_reused(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    first = (await _request(client, user_a, resume_id, job_id)).json()

    def down(request: LLMRequest) -> dict:
        raise AIProviderError("fora do ar")

    llm = FakeLLMProvider(handlers={"analyze_fit": down})
    assert await _runner(db_session, user_a, llm).run(uuid.UUID(first["id"])) == "failed"

    detail = (await client.get(f"/api/v1/analyses/{first['id']}", headers=user_a.headers)).json()
    assert detail["error"] == MSG_AI_UNAVAILABLE
    assert detail["result"] is None

    again = (await _request(client, user_a, resume_id, job_id)).json()
    assert again["id"] != first["id"]


async def test_invented_quote_is_retried_with_feedback(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    created = (await _request(client, user_a, resume_id, job_id)).json()
    calls: list[LLMRequest] = []

    def flaky(request: LLMRequest) -> dict:
        calls.append(request)
        output = analyze_fit(request)
        if len(calls) == 1:
            output["verdicts"][0]["evidence"][0]["quote"] = "Liderei squads de 20 pessoas."
        return output

    llm = FakeLLMProvider(handlers={"analyze_fit": flaky})
    assert await _runner(db_session, user_a, llm).run(uuid.UUID(created["id"])) == "done"
    assert len(calls) == 2
    feedback = " ".join(calls[1].feedback or ())
    assert "cópia literal" in feedback
    assert "Liderei" not in feedback


async def test_invented_quote_twice_fails_with_clear_message(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    created = (await _request(client, user_a, resume_id, job_id)).json()

    def liar(request: LLMRequest) -> dict:
        output = analyze_fit(request)
        output["verdicts"][0]["evidence"][0]["quote"] = "Liderei squads de 20 pessoas."
        return output

    llm = FakeLLMProvider(handlers={"analyze_fit": liar})
    assert await _runner(db_session, user_a, llm).run(uuid.UUID(created["id"])) == "failed"
    detail = (await client.get(f"/api/v1/analyses/{created['id']}", headers=user_a.headers)).json()
    assert detail["status"] == "failed"
    assert detail["error"] == MSG_INVALID_OUTPUT
    assert detail["score"] is None


async def test_unexpected_error_marks_failed(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    created = (await _request(client, user_a, resume_id, job_id)).json()

    def boom(request: LLMRequest) -> dict:
        raise RuntimeError("bug")

    llm = FakeLLMProvider(handlers={"analyze_fit": boom})
    assert await _runner(db_session, user_a, llm).run(uuid.UUID(created["id"])) == "failed"
    detail = (await client.get(f"/api/v1/analyses/{created['id']}", headers=user_a.headers)).json()
    assert detail["error"] == MSG_INTERNAL


async def test_runner_ignores_missing_and_finished(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    llm = FakeLLMProvider()
    assert await _runner(db_session, user_a, llm).run(uuid.uuid4()) is None

    resume_id, job_id = await _setup(client, user_a)
    created = (await _request(client, user_a, resume_id, job_id)).json()
    await _runner(db_session, user_a, llm).run(uuid.UUID(created["id"]))
    calls = len(llm.requests)
    assert await _runner(db_session, user_a, llm).run(uuid.UUID(created["id"])) == "done"
    assert len(llm.requests) == calls


async def test_runner_fails_when_job_was_deleted(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    created = (await _request(client, user_a, resume_id, job_id)).json()
    # CASCADE apaga a análise junto com a vaga: o worker só não encontra nada.
    await client.delete(f"/api/v1/jobs/{job_id}", headers=user_a.headers)
    runner = _runner(db_session, user_a, FakeLLMProvider())
    assert await runner.run(uuid.UUID(created["id"])) is None


async def test_list_filters_by_job(client: AsyncClient, user_a: AuthedUser) -> None:
    resume_id, job_id = await _setup(client, user_a)
    _, other_job = await _setup(client, user_a)
    first = (await _request(client, user_a, resume_id, job_id)).json()
    second = (await _request(client, user_a, resume_id, other_job)).json()

    # Mesmo texto de vaga, mas outra vaga: não reaproveita (a análise pertence à vaga).
    assert second["id"] != first["id"]
    listing = await client.get("/api/v1/analyses", headers=user_a.headers)
    assert {a["id"] for a in listing.json()} == {first["id"], second["id"]}
    filtered = await client.get(
        "/api/v1/analyses", params={"job_id": job_id}, headers=user_a.headers
    )
    assert [a["id"] for a in filtered.json()] == [first["id"]]


async def test_isolation_between_users(
    client: AsyncClient, user_a: AuthedUser, user_b: AuthedUser
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    created = (await _request(client, user_a, resume_id, job_id)).json()
    b_resume, b_job = await _setup(client, user_b)

    other = await client.get(f"/api/v1/analyses/{created['id']}", headers=user_b.headers)
    assert other.status_code == 404
    assert (await client.get("/api/v1/analyses", headers=user_b.headers)).json() == []
    # B não pode analisar o currículo nem a vaga de A, nem misturar com os seus.
    for r, j in ((resume_id, job_id), (b_resume, job_id), (resume_id, b_job)):
        response = await _request(client, user_b, r, j)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"
