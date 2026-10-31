import pytest
from httpx import AsyncClient

from app.core.logging import REQUEST_ID_HEADER


async def test_generates_request_id_when_missing(client: AsyncClient) -> None:
    response = await client.get("/api/v1/does-not-exist")

    request_id = response.headers[REQUEST_ID_HEADER]
    assert len(request_id) == 32


async def test_reuses_valid_request_id_from_client(client: AsyncClient) -> None:
    response = await client.get("/api/v1/x", headers={REQUEST_ID_HEADER: "abc-123_DEF"})

    assert response.headers[REQUEST_ID_HEADER] == "abc-123_DEF"


@pytest.mark.parametrize("bad", ["a b", "x" * 65, "evil\ninjected", ""])
async def test_replaces_invalid_request_id(client: AsyncClient, bad: str) -> None:
    response = await client.get("/api/v1/x", headers={REQUEST_ID_HEADER: bad})

    assert response.headers[REQUEST_ID_HEADER] != bad
    assert len(response.headers[REQUEST_ID_HEADER]) == 32
