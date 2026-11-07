import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.errors import AIProviderError
from app.ai.fake_llm import FakeLLMProvider
from app.ai.llm import LLMRequest
from app.repositories.jobs import JobRepository
from app.services.job_extraction import ensure_extracted, run_extraction_task
from app.worker.queue import EXTRACT_JOB_TASK, InMemoryTaskQueue
from tests.integration.conftest import AuthedUser

pytestmark = pytest.mark.integration

JOB_TEXT = """Desenvolvedora Backend Pleno
Empresa: Exemplo S.A.

Requisitos
- Python
- PostgreSQL

Diferenciais
- Redis
"""


async def _create(client: AsyncClient, user: AuthedUser, **extra: str) -> dict:
    response = await client.post(
        "/api/v1/jobs", json={"raw_text": JOB_TEXT, **extra}, headers=user.headers
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_enqueues_extraction_and_lists(
    client: AsyncClient, user_a: AuthedUser, task_queue: InMemoryTaskQueue
) -> None:
    created = await _create(client, user_a)

    assert created["title"] == "Desenvolvedora Backend Pleno"
    assert created["company"] is None
    assert created["extraction_status"] == "pending"
    assert task_queue.sent == [(EXTRACT_JOB_TASK, (created["id"], str(user_a.id)))]

    listing = await client.get("/api/v1/jobs", headers=user_a.headers)
    assert [j["id"] for j in listing.json()] == [created["id"]]

    detail = await client.get(f"/api/v1/jobs/{created['id']}", headers=user_a.headers)
    assert detail.status_code == 200
    assert detail.json()["extracted"] is None
    assert detail.json()["raw_text"].startswith("Desenvolvedora")


async def test_explicit_title_and_company(client: AsyncClient, user_a: AuthedUser) -> None:
    created = await _create(client, user_a, title=" Backend ", company="Acme")
    assert created["title"] == "Backend"
    assert created["company"] == "Acme"


async def test_short_text_is_rejected(client: AsyncClient, user_a: AuthedUser) -> None:
    response = await client.post("/api/v1/jobs", json={"raw_text": "curto"}, headers=user_a.headers)
    assert response.status_code == 422


async def test_extraction_runs_and_detail_shows_requirements(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    created = await _create(client, user_a)
    job_id = uuid.UUID(created["id"])

    assert await run_extraction_task(db_session, user_a.id, job_id, FakeLLMProvider())

    detail = (await client.get(f"/api/v1/jobs/{job_id}", headers=user_a.headers)).json()
    assert detail["extraction_status"] == "done"
    reqs = detail["extracted"]["requirements"]
    assert [(r["id"], r["text"], r["kind"]) for r in reqs] == [
        ("R1", "Python", "required"),
        ("R2", "PostgreSQL", "required"),
        ("R3", "Redis", "nice_to_have"),
    ]


async def test_extraction_is_idempotent(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    job_id = uuid.UUID((await _create(client, user_a))["id"])
    llm = FakeLLMProvider()

    first = await ensure_extracted(db_session, user_a.id, job_id, llm)
    second = await ensure_extracted(db_session, user_a.id, job_id, llm)

    assert first == second
    assert len(llm.requests) == 1


async def test_extraction_failure_leaves_job_unextracted_with_error(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    job_id = uuid.UUID((await _create(client, user_a))["id"])

    def broken(request: LLMRequest) -> dict:
        raise AIProviderError()

    ok = await run_extraction_task(
        db_session, user_a.id, job_id, FakeLLMProvider(handlers={"extract_requirements": broken})
    )
    invalid = await run_extraction_task(
        db_session, user_a.id, job_id, FakeLLMProvider(scripted=["{}", "{}"])
    )

    assert ok is False
    assert invalid is False
    job = await JobRepository(db_session, user_a.id).get(job_id)
    assert job is not None
    assert job.extracted is None
    assert job.extraction_error is not None


async def test_extraction_of_other_users_job_does_nothing(
    client: AsyncClient, user_a: AuthedUser, user_b: AuthedUser, db_session: AsyncSession
) -> None:
    job_id = uuid.UUID((await _create(client, user_a))["id"])
    llm = FakeLLMProvider()

    assert await run_extraction_task(db_session, user_b.id, job_id, llm) is False
    assert llm.requests == []


async def test_isolation_between_users(
    client: AsyncClient, user_a: AuthedUser, user_b: AuthedUser
) -> None:
    created = await _create(client, user_a)
    url = f"/api/v1/jobs/{created['id']}"

    assert (await client.get("/api/v1/jobs", headers=user_b.headers)).json() == []
    assert (await client.get(url, headers=user_b.headers)).status_code == 404
    assert (await client.delete(url, headers=user_b.headers)).status_code == 404
    assert (await client.get(url, headers=user_a.headers)).status_code == 200


async def test_delete(client: AsyncClient, user_a: AuthedUser) -> None:
    created = await _create(client, user_a)
    url = f"/api/v1/jobs/{created['id']}"

    assert (await client.delete(url, headers=user_a.headers)).status_code == 204
    assert (await client.get(url, headers=user_a.headers)).status_code == 404
    assert (await client.delete(url, headers=user_a.headers)).status_code == 404


async def test_failed_extraction_is_visible_and_retry_requeues(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession, task_queue: InMemoryTaskQueue
) -> None:
    created = await _create(client, user_a)
    job_id = uuid.UUID(created["id"])

    def broken(request: LLMRequest) -> dict:
        raise AIProviderError()

    assert not await run_extraction_task(
        db_session, user_a.id, job_id, FakeLLMProvider(handlers={"extract_requirements": broken})
    )
    detail = (await client.get(f"/api/v1/jobs/{job_id}", headers=user_a.headers)).json()
    assert detail["extraction_status"] == "failed"
    assert detail["extracted"] is None

    retry = await client.post(f"/api/v1/jobs/{job_id}/extract", headers=user_a.headers)
    assert retry.status_code == 202
    assert retry.json()["extraction_status"] == "pending"
    assert task_queue.sent[-1] == (EXTRACT_JOB_TASK, (str(job_id), str(user_a.id)))

    assert await run_extraction_task(db_session, user_a.id, job_id, FakeLLMProvider())
    job = await JobRepository(db_session, user_a.id).get(job_id)
    assert job is not None
    assert job.extraction_error is None
    detail = (await client.get(f"/api/v1/jobs/{job_id}", headers=user_a.headers)).json()
    assert detail["extraction_status"] == "done"


async def test_retry_on_extracted_job_changes_nothing(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession, task_queue: InMemoryTaskQueue
) -> None:
    created = await _create(client, user_a)
    job_id = uuid.UUID(created["id"])
    assert await run_extraction_task(db_session, user_a.id, job_id, FakeLLMProvider())
    sent_before = len(task_queue.sent)

    retry = await client.post(f"/api/v1/jobs/{job_id}/extract", headers=user_a.headers)

    assert retry.status_code == 202
    assert retry.json()["extraction_status"] == "done"
    assert len(task_queue.sent) == sent_before


async def test_retry_of_other_users_job_is_not_found(
    client: AsyncClient, user_a: AuthedUser, user_b: AuthedUser
) -> None:
    job_id = (await _create(client, user_a))["id"]

    response = await client.post(f"/api/v1/jobs/{job_id}/extract", headers=user_b.headers)

    assert response.status_code == 404
