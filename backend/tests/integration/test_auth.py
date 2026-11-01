import uuid
from datetime import timedelta

import pytest
from httpx import AsyncClient, Response
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import security
from app.core.config import get_settings
from app.core.metrics import AUTH_LOGIN_FAILURES, AUTH_REFRESH_REUSE_DETECTED
from app.models.mixins import utcnow
from app.models.refresh_token import RefreshToken
from app.services import auth as auth_service
from tests.integration.conftest import PASSWORD, AuthedUser, register
from tests.metrics_helpers import counter_value

pytestmark = pytest.mark.integration

AUTH = "/api/v1/auth"
COOKIE = get_settings().refresh_cookie_name


def _set_cookie_header(response: Response) -> str:
    headers = [h for h in response.headers.get_list("set-cookie") if h.startswith(f"{COOKIE}=")]
    assert len(headers) == 1, response.headers.get_list("set-cookie")
    return headers[0]


async def _refresh_with(client: AsyncClient, token: str) -> Response:
    """Refresh com um token específico, ignorando o que estiver no cookie jar."""
    client.cookies.clear()
    return await client.post(f"{AUTH}/refresh", headers={"Cookie": f"{COOKIE}={token}"})


async def _token_count(session: AsyncSession, user_id: uuid.UUID) -> int:
    result = await session.execute(
        select(func.count()).select_from(RefreshToken).where(RefreshToken.user_id == user_id)
    )
    return result.scalar_one()


# ------------------------------------------------------------------ cadastro


async def test_register_creates_account_and_sets_refresh_cookie(client: AsyncClient) -> None:
    response = await client.post(
        f"{AUTH}/register", json={"email": "  Ana@Exemplo.COM ", "password": PASSWORD}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 900
    assert body["user"]["email"] == "ana@exemplo.com"
    assert "password_hash" not in body["user"]
    assert "refresh" not in body

    cookie = _set_cookie_header(response).lower()
    assert "httponly" in cookie
    assert "secure" in cookie
    assert "samesite=strict" in cookie
    assert "path=/api/v1/auth" in cookie
    assert f"max-age={7 * 24 * 60 * 60}" in cookie


async def test_register_rejects_duplicate_email(client: AsyncClient, user_a: AuthedUser) -> None:
    response = await client.post(
        f"{AUTH}/register", json={"email": user_a.email.upper(), "password": PASSWORD}
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "email_taken"


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"email": "sem-arroba", "password": PASSWORD}, id="invalid-email"),
        pytest.param({"email": "a@b.co", "password": "curta"}, id="short-password"),
        pytest.param({"email": "a@b.co", "password": "x" * 129}, id="long-password"),
        pytest.param({"email": "a@b.co"}, id="missing-password"),
    ],
)
async def test_register_validates_input(client: AsyncClient, payload: dict[str, str]) -> None:
    response = await client.post(f"{AUTH}/register", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


# ------------------------------------------------------------------ login


async def test_login_returns_tokens(client: AsyncClient, user_a: AuthedUser) -> None:
    client.cookies.clear()

    response = await client.post(
        f"{AUTH}/login", json={"email": "ANA@exemplo.com", "password": PASSWORD}
    )

    assert response.status_code == 200
    assert response.json()["user"]["id"] == str(user_a.id)
    assert _set_cookie_header(response)


async def test_login_errors_are_generic(client: AsyncClient, user_a: AuthedUser) -> None:
    wrong_password = await client.post(
        f"{AUTH}/login", json={"email": user_a.email, "password": "senha-errada"}
    )
    unknown_email = await client.post(
        f"{AUTH}/login", json={"email": "ninguem@exemplo.com", "password": PASSWORD}
    )

    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.json()["error"]["code"] == "invalid_credentials"


async def test_login_failures_are_counted(client: AsyncClient, user_a: AuthedUser) -> None:
    before = counter_value(AUTH_LOGIN_FAILURES)

    await client.post(f"{AUTH}/login", json={"email": user_a.email, "password": "senha-errada"})
    await client.post(f"{AUTH}/login", json={"email": "ninguem@exemplo.com", "password": PASSWORD})
    await client.post(f"{AUTH}/login", json={"email": user_a.email, "password": PASSWORD})

    assert counter_value(AUTH_LOGIN_FAILURES) - before == 2


async def test_login_with_unknown_email_still_verifies_a_hash(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Tempo constante (S5): e-mail inexistente também paga o custo do argon2."""
    calls: list[str] = []
    real_verify = security.verify_password

    async def spy(password_hash: str, password: str) -> bool:
        calls.append(password_hash)
        return await real_verify(password_hash, password)

    monkeypatch.setattr(auth_service, "verify_password", spy)

    response = await client.post(
        f"{AUTH}/login", json={"email": "ninguem@exemplo.com", "password": PASSWORD}
    )

    assert response.status_code == 401
    assert calls == [security.dummy_password_hash()]


async def test_login_purges_expired_refresh_tokens(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    await db_session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_a.id)
        .values(expires_at=utcnow() - timedelta(days=1))
    )

    await client.post(f"{AUTH}/login", json={"email": user_a.email, "password": PASSWORD})

    assert await _token_count(db_session, user_a.id) == 1


# ------------------------------------------------------------------ usuário atual


async def test_me_returns_the_authenticated_user(
    client: AsyncClient, user_a: AuthedUser, user_b: AuthedUser
) -> None:
    me_a = await client.get(f"{AUTH}/me", headers=user_a.headers)
    me_b = await client.get(f"{AUTH}/me", headers=user_b.headers)

    assert me_a.json()["id"] == str(user_a.id)
    assert me_b.json()["id"] == str(user_b.id)


async def test_me_rejects_invalid_token(client: AsyncClient) -> None:
    response = await client.get(f"{AUTH}/me", headers={"Authorization": "Bearer lixo"})

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"


# ------------------------------------------------------------------ refresh


async def test_refresh_rotates_the_token(client: AsyncClient, user_a: AuthedUser) -> None:
    first = client.cookies[COOKIE]

    response = await client.post(f"{AUTH}/refresh")

    assert response.status_code == 200
    second = client.cookies[COOKIE]
    assert second != first
    new_access = response.json()["access_token"]
    me = await client.get(f"{AUTH}/me", headers={"Authorization": f"Bearer {new_access}"})
    assert me.json()["id"] == str(user_a.id)


async def test_refresh_without_cookie_is_rejected(client: AsyncClient) -> None:
    response = await client.post(f"{AUTH}/refresh")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_refresh_token"


async def test_refresh_with_unknown_token_clears_cookie(client: AsyncClient) -> None:
    response = await _refresh_with(client, "token-que-nao-existe")

    assert response.status_code == 401
    assert "max-age=0" in _set_cookie_header(response).lower()


async def test_reusing_a_rotated_token_revokes_the_whole_family(
    client: AsyncClient, user_a: AuthedUser
) -> None:
    stolen = client.cookies[COOKIE]
    rotated = await _refresh_with(client, stolen)
    current = rotated.cookies[COOKIE]
    reuse_before = counter_value(AUTH_REFRESH_REUSE_DETECTED)

    reuse = await _refresh_with(client, stolen)
    after_reuse = await _refresh_with(client, current)

    assert reuse.status_code == 401
    assert after_reuse.status_code == 401, "o token legítimo da família também morre"
    assert counter_value(AUTH_REFRESH_REUSE_DETECTED) - reuse_before == 1


async def test_reuse_in_one_session_does_not_affect_other_sessions(
    client: AsyncClient, user_a: AuthedUser
) -> None:
    session_1 = client.cookies[COOKIE]
    login = await client.post(f"{AUTH}/login", json={"email": user_a.email, "password": PASSWORD})
    session_2 = login.cookies[COOKIE]

    await _refresh_with(client, session_1)
    await _refresh_with(client, session_1)  # reuso: revoga só a família 1

    assert (await _refresh_with(client, session_2)).status_code == 200


async def test_expired_refresh_token_is_rejected(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    token = client.cookies[COOKIE]
    await db_session.execute(
        update(RefreshToken)
        .where(RefreshToken.user_id == user_a.id)
        .values(expires_at=utcnow() - timedelta(seconds=1))
    )

    response = await _refresh_with(client, token)

    assert response.status_code == 401


# ------------------------------------------------------------------ logout


async def test_logout_revokes_the_session(client: AsyncClient, user_a: AuthedUser) -> None:
    token = client.cookies[COOKIE]

    response = await client.post(f"{AUTH}/logout")

    assert response.status_code == 204
    assert "max-age=0" in _set_cookie_header(response).lower()
    assert (await _refresh_with(client, token)).status_code == 401


@pytest.mark.parametrize("cookie", [None, "token-que-nao-existe"])
async def test_logout_is_idempotent(client: AsyncClient, cookie: str | None) -> None:
    headers = {"Cookie": f"{COOKIE}={cookie}"} if cookie else {}

    response = await client.post(f"{AUTH}/logout", headers=headers)

    assert response.status_code == 204


# ------------------------------------------------------------------ exclusão de conta


async def test_delete_account_requires_the_password(
    client: AsyncClient, user_a: AuthedUser
) -> None:
    response = await client.request(
        "DELETE", f"{AUTH}/me", json={"password": "senha-errada"}, headers=user_a.headers
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "invalid_password"
    assert (await client.get(f"{AUTH}/me", headers=user_a.headers)).status_code == 200


async def test_delete_account_removes_user_and_sessions(
    client: AsyncClient, user_a: AuthedUser, db_session: AsyncSession
) -> None:
    refresh_token = client.cookies[COOKIE]

    response = await client.request(
        "DELETE", f"{AUTH}/me", json={"password": PASSWORD}, headers=user_a.headers
    )

    assert response.status_code == 204
    assert (await client.get(f"{AUTH}/me", headers=user_a.headers)).status_code == 401
    assert (await _refresh_with(client, refresh_token)).status_code == 401
    login = await client.post(f"{AUTH}/login", json={"email": user_a.email, "password": PASSWORD})
    assert login.status_code == 401
    assert await _token_count(db_session, user_a.id) == 0


async def test_deleting_one_account_does_not_touch_another(
    client: AsyncClient, user_a: AuthedUser
) -> None:
    user_b = await register(client, "bruno@exemplo.com")
    b_refresh = client.cookies[COOKIE]

    await client.request(
        "DELETE", f"{AUTH}/me", json={"password": PASSWORD}, headers=user_a.headers
    )

    assert (await client.get(f"{AUTH}/me", headers=user_b.headers)).status_code == 200
    assert (await _refresh_with(client, b_refresh)).status_code == 200
