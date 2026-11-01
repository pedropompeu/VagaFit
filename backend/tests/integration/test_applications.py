from datetime import date

import pytest
from httpx import AsyncClient

from tests.integration.conftest import AuthedUser
from tests.integration.test_analyses import _request, _setup

pytestmark = pytest.mark.integration

URL = "/api/v1/applications"


async def _job(client: AsyncClient, user: AuthedUser, title: str = "Backend") -> str:
    response = await client.post(
        "/api/v1/jobs",
        json={"raw_text": "Vaga de backend com Python e PostgreSQL.", "title": title},
        headers=user.headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


async def _apply(client: AsyncClient, user: AuthedUser, job_id: str, **extra: object):
    return await client.post(URL, json={"job_id": job_id, **extra}, headers=user.headers)


async def test_create_with_defaults(client: AsyncClient, user_a: AuthedUser) -> None:
    job_id = await _job(client, user_a, "Dev Python")

    response = await _apply(client, user_a, job_id, platform=" LinkedIn ", salary_expectation=9000)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["status"] == "sent"
    assert body["applied_at"] == date.today().isoformat()
    assert body["platform"] == "LinkedIn"
    assert body["salary_expectation"] == 9000
    assert body["job"] == {"id": job_id, "title": "Dev Python", "company": None}
    assert body["analysis_id"] is None


async def test_one_application_per_job(client: AsyncClient, user_a: AuthedUser) -> None:
    job_id = await _job(client, user_a)
    assert (await _apply(client, user_a, job_id)).status_code == 201

    again = await _apply(client, user_a, job_id)
    assert again.status_code == 409
    assert again.json()["error"]["code"] == "conflict"


async def test_links_analysis_of_same_job_only(client: AsyncClient, user_a: AuthedUser) -> None:
    resume_id, job_id = await _setup(client, user_a)
    analysis = (await _request(client, user_a, resume_id, job_id)).json()
    other_job = await _job(client, user_a, "Outra")

    wrong = await _apply(client, user_a, other_job, analysis_id=analysis["id"])
    assert wrong.status_code == 422
    assert wrong.json()["error"]["code"] == "invalid_analysis"

    ok = await _apply(client, user_a, job_id, analysis_id=analysis["id"])
    assert ok.status_code == 201
    assert ok.json()["analysis_id"] == analysis["id"]

    # Apagar a análise mantém a candidatura (SET NULL).
    app_id = ok.json()["id"]
    await client.delete(f"/api/v1/resumes/{resume_id}", headers=user_a.headers)
    detail = await client.get(f"{URL}/{app_id}", headers=user_a.headers)
    assert detail.json()["analysis_id"] is None


async def test_filter_by_status_and_order(client: AsyncClient, user_a: AuthedUser) -> None:
    job_a, job_b, job_c = [await _job(client, user_a, t) for t in "ABC"]
    old = (await _apply(client, user_a, job_a, applied_at="2026-10-01")).json()
    new = (await _apply(client, user_a, job_b, status="interview")).json()
    rejected = (
        await _apply(client, user_a, job_c, status="rejected", applied_at="2026-10-15")
    ).json()

    listing = await client.get(URL, headers=user_a.headers)
    assert [a["id"] for a in listing.json()] == [new["id"], rejected["id"], old["id"]]

    filtered = await client.get(
        URL, params=[("status", "sent"), ("status", "interview")], headers=user_a.headers
    )
    assert [a["id"] for a in filtered.json()] == [new["id"], old["id"]]

    invalid = await client.get(URL, params={"status": "Enviada"}, headers=user_a.headers)
    assert invalid.status_code == 422


async def test_partial_update(client: AsyncClient, user_a: AuthedUser) -> None:
    created = (
        await _apply(client, user_a, await _job(client, user_a), platform="Gupy", next_step="Teste")
    ).json()

    response = await client.patch(
        f"{URL}/{created['id']}",
        json={"status": "tech_test", "next_step": None},
        headers=user_a.headers,
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "tech_test"
    assert body["next_step"] is None
    assert body["platform"] == "Gupy"
    assert body["updated_at"] >= created["updated_at"]


@pytest.mark.parametrize(
    "payload",
    [{"status": None}, {"applied_at": None}, {"status": "Enviada"}, {"salary_expectation": -1}],
)
async def test_update_rejects_invalid(
    client: AsyncClient, user_a: AuthedUser, payload: dict
) -> None:
    created = (await _apply(client, user_a, await _job(client, user_a))).json()
    response = await client.patch(f"{URL}/{created['id']}", json=payload, headers=user_a.headers)
    assert response.status_code == 422


async def test_update_checks_analysis_job(client: AsyncClient, user_a: AuthedUser) -> None:
    resume_id, job_id = await _setup(client, user_a)
    analysis = (await _request(client, user_a, resume_id, job_id)).json()
    created = (await _apply(client, user_a, await _job(client, user_a))).json()

    response = await client.patch(
        f"{URL}/{created['id']}", json={"analysis_id": analysis["id"]}, headers=user_a.headers
    )
    assert response.status_code == 422


async def test_delete(client: AsyncClient, user_a: AuthedUser) -> None:
    created = (await _apply(client, user_a, await _job(client, user_a))).json()
    deleted = await client.delete(f"{URL}/{created['id']}", headers=user_a.headers)
    assert deleted.status_code == 204
    assert (await client.get(f"{URL}/{created['id']}", headers=user_a.headers)).status_code == 404


async def test_deleting_job_deletes_application(client: AsyncClient, user_a: AuthedUser) -> None:
    job_id = await _job(client, user_a)
    created = (await _apply(client, user_a, job_id)).json()
    await client.delete(f"/api/v1/jobs/{job_id}", headers=user_a.headers)
    assert (await client.get(f"{URL}/{created['id']}", headers=user_a.headers)).status_code == 404


async def test_isolation_between_users(
    client: AsyncClient, user_a: AuthedUser, user_b: AuthedUser
) -> None:
    resume_id, job_id = await _setup(client, user_a)
    analysis = (await _request(client, user_a, resume_id, job_id)).json()
    created = (await _apply(client, user_a, job_id)).json()
    b_job = await _job(client, user_b)
    path = f"{URL}/{created['id']}"

    assert (await client.get(path, headers=user_b.headers)).status_code == 404
    patch = await client.patch(path, json={"status": "offer"}, headers=user_b.headers)
    assert patch.status_code == 404
    assert (await client.delete(path, headers=user_b.headers)).status_code == 404
    assert (await client.get(URL, headers=user_b.headers)).json() == []
    # B não se candidata à vaga de A nem liga a análise de A à própria vaga.
    assert (await _apply(client, user_b, job_id)).status_code == 404
    assert (await _apply(client, user_b, b_job, analysis_id=analysis["id"])).status_code == 404

    still = await client.get(path, headers=user_a.headers)
    assert still.json()["status"] == "sent"
