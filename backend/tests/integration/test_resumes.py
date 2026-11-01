import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import FakeEmbeddingProvider
from app.repositories.resumes import ResumeRepository
from tests.integration.conftest import AuthedUser
from tests.pdf_factory import make_pdf

pytestmark = pytest.mark.integration

RESUME_TEXT = """RESUMO
Desenvolvedora backend com foco em Python.

EXPERIÊNCIA
Desenvolvedora Backend, Acme Ltda, 2021-2024
- Criei APIs REST em FastAPI.
- Usei PostgreSQL e Redis em produção.

FORMAÇÃO
Ciência da Computação, Universidade Exemplo, 2017
"""


async def _create(client: AsyncClient, user: AuthedUser, title: str = "Backend") -> dict:
    response = await client.post(
        "/api/v1/resumes", data={"title": title, "text": RESUME_TEXT}, headers=user.headers
    )
    assert response.status_code == 201, response.text
    return response.json()


async def test_create_from_text_list_and_detail(client: AsyncClient, user_a: AuthedUser) -> None:
    created = await _create(client, user_a)
    assert created["title"] == "Backend"
    assert created["chunk_count"] == 3

    listing = await client.get("/api/v1/resumes", headers=user_a.headers)
    assert listing.status_code == 200
    assert [r["id"] for r in listing.json()] == [created["id"]]
    assert listing.json()[0]["chunk_count"] == 3

    detail = await client.get(f"/api/v1/resumes/{created['id']}", headers=user_a.headers)
    assert detail.status_code == 200
    body = detail.json()
    assert body["raw_text"].startswith("RESUMO")
    assert [c["ordinal"] for c in body["chunks"]] == [0, 1, 2]
    assert body["chunks"][1]["content"].startswith("EXPERIÊNCIA\nDesenvolvedora Backend")


async def test_create_from_pdf(client: AsyncClient, user_a: AuthedUser) -> None:
    pdf = make_pdf([["EXPERIENCIA", "Dev Python, Acme, 2020-2024", "- Criei APIs em FastAPI."]])
    response = await client.post(
        "/api/v1/resumes",
        data={"title": "PDF"},
        files={"file": ("cv.pdf", pdf, "application/pdf")},
        headers=user_a.headers,
    )
    assert response.status_code == 201, response.text
    detail = await client.get(f"/api/v1/resumes/{response.json()['id']}", headers=user_a.headers)
    assert "Criei APIs em FastAPI." in detail.json()["chunks"][0]["content"]


async def test_preview_does_not_save(client: AsyncClient, user_a: AuthedUser) -> None:
    response = await client.post(
        "/api/v1/resumes/preview", data={"text": RESUME_TEXT}, headers=user_a.headers
    )
    assert response.status_code == 200
    assert response.json()["chunk_count"] == 3
    assert response.json()["chunks"][0]["estimated_tokens"] > 0

    listing = await client.get("/api/v1/resumes", headers=user_a.headers)
    assert listing.json() == []


@pytest.mark.parametrize(
    ("data", "files", "status", "code"),
    [
        ({"title": "x"}, None, 422, "invalid_resume"),
        ({"title": "x", "text": "   "}, None, 422, "invalid_resume"),
        (
            {"title": "x", "text": "abc"},
            {"file": ("cv.pdf", make_pdf([["a"]]), "application/pdf")},
            422,
            "invalid_resume",
        ),
        ({"title": "x"}, {"file": ("cv.docx", b"PK\x03\x04", "application/pdf")}, 415, None),
        ({"title": "x"}, {"file": ("cv.pdf", b"%PDF-1.4 lixo", "application/pdf")}, 422, None),
        ({"text": "abc"}, None, 422, "validation_error"),
    ],
)
async def test_invalid_input(
    client: AsyncClient,
    user_a: AuthedUser,
    data: dict[str, str],
    files: dict | None,
    status: int,
    code: str | None,
) -> None:
    response = await client.post("/api/v1/resumes", data=data, files=files, headers=user_a.headers)
    assert response.status_code == status, response.text
    if code is not None:
        assert response.json()["error"]["code"] == code


async def test_rejects_upload_over_limit(
    client: AsyncClient, user_a: AuthedUser, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "resume_max_upload_bytes", 1024)
    big = b"%PDF-1.4\n" + b"0" * 4096
    response = await client.post(
        "/api/v1/resumes",
        data={"title": "x"},
        files={"file": ("cv.pdf", big, "application/pdf")},
        headers=user_a.headers,
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "payload_too_large"


async def test_rejects_text_over_char_limit(
    client: AsyncClient, user_a: AuthedUser, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.core.config import get_settings

    monkeypatch.setattr(get_settings(), "resume_max_text_chars", 10)
    response = await client.post(
        "/api/v1/resumes", data={"title": "x", "text": "a" * 50}, headers=user_a.headers
    )
    assert response.status_code == 422
    assert "limite" in response.json()["error"]["message"]


async def test_delete(client: AsyncClient, user_a: AuthedUser) -> None:
    created = await _create(client, user_a)
    url = f"/api/v1/resumes/{created['id']}"

    assert (await client.delete(url, headers=user_a.headers)).status_code == 204
    assert (await client.get(url, headers=user_a.headers)).status_code == 404
    assert (await client.delete(url, headers=user_a.headers)).status_code == 404


async def test_isolation_between_users(
    client: AsyncClient, user_a: AuthedUser, user_b: AuthedUser
) -> None:
    created = await _create(client, user_a)
    url = f"/api/v1/resumes/{created['id']}"

    assert (await client.get("/api/v1/resumes", headers=user_b.headers)).json() == []
    for method in ("GET", "DELETE"):
        response = await client.request(method, url, headers=user_b.headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "not_found"

    assert (await client.get(url, headers=user_a.headers)).status_code == 200


async def test_unknown_resume_is_404(client: AsyncClient, user_a: AuthedUser) -> None:
    response = await client.get(f"/api/v1/resumes/{uuid.uuid4()}", headers=user_a.headers)
    assert response.status_code == 404


async def test_nearest_chunks_respects_owner(
    client: AsyncClient, user_a: AuthedUser, user_b: AuthedUser, db_session: AsyncSession
) -> None:
    created = await _create(client, user_a)
    resume_id = uuid.UUID(created["id"])
    query = FakeEmbeddingProvider.vector("APIs REST em FastAPI")

    owner = ResumeRepository(db_session, user_a.id)
    matches = await owner.nearest_chunks(resume_id, query, k=3)
    assert len(matches) == 3
    assert "FastAPI" in matches[0].chunk.content
    assert matches[0].distance <= matches[1].distance
    assert [c.ordinal for c in await owner.get_chunks(resume_id)] == [0, 1, 2]

    stranger = ResumeRepository(db_session, user_b.id)
    assert await stranger.nearest_chunks(resume_id, query, k=3) == []
    assert await stranger.get_chunks(resume_id) == []
