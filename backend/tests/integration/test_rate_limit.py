import pytest
from httpx import AsyncClient

from tests.integration.conftest import PASSWORD

pytestmark = [pytest.mark.integration, pytest.mark.usefixtures("rate_limited")]

AUTH = "/api/v1/auth"


async def test_login_is_limited_to_5_per_minute(client: AsyncClient) -> None:
    payload = {"email": "ninguem@exemplo.com", "password": PASSWORD}
    statuses = [(await client.post(f"{AUTH}/login", json=payload)).status_code for _ in range(5)]

    blocked = await client.post(f"{AUTH}/login", json=payload)

    assert statuses == [401] * 5
    assert blocked.status_code == 429
    assert blocked.json()["error"]["code"] == "rate_limited"
    assert int(blocked.headers["retry-after"]) > 0


async def test_register_is_limited_to_3_per_minute(client: AsyncClient) -> None:
    for i in range(3):
        response = await client.post(
            f"{AUTH}/register", json={"email": f"u{i}@exemplo.com", "password": PASSWORD}
        )
        assert response.status_code == 201

    blocked = await client.post(
        f"{AUTH}/register", json={"email": "u9@exemplo.com", "password": PASSWORD}
    )

    assert blocked.status_code == 429
