import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.core.config import Settings
from app.core.security import (
    JWT_ALGORITHM,
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    hash_refresh_token,
    new_refresh_token,
    password_needs_rehash,
    verify_password,
)

SECRET = "s" * 40


@pytest.fixture
def settings() -> Settings:
    return Settings(jwt_secret=SECRET)  # type: ignore[arg-type]


def _token(payload: dict[str, object], secret: str = SECRET) -> str:
    return jwt.encode(payload, secret, algorithm=JWT_ALGORITHM)


def _claims(**overrides: object) -> dict[str, object]:
    now = datetime.now(UTC)
    claims: dict[str, object] = {
        "sub": str(uuid.uuid4()),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=5),
        "jti": "abc",
    }
    claims.update(overrides)
    return claims


async def test_password_hash_is_argon2id_and_verifies() -> None:
    hashed = await hash_password("uma-senha-longa")

    assert hashed.startswith("$argon2id$")
    assert await verify_password(hashed, "uma-senha-longa")
    assert not await verify_password(hashed, "outra-senha")
    assert not password_needs_rehash(hashed)


async def test_verify_password_rejects_malformed_hash() -> None:
    assert not await verify_password("nao-e-um-hash", "qualquer")


def test_access_token_roundtrip(settings: Settings) -> None:
    user_id = uuid.uuid4()

    access = create_access_token(user_id, settings)

    assert access.expires_in == 15 * 60
    assert decode_access_token(access.token, settings) == user_id
    claims = jwt.decode(access.token, SECRET, algorithms=[JWT_ALGORITHM])
    assert claims["type"] == "access"
    assert set(claims) == {"sub", "type", "iat", "exp", "jti"}


@pytest.mark.parametrize(
    "token",
    [
        pytest.param(_token(_claims(exp=datetime.now(UTC) - timedelta(seconds=1))), id="expired"),
        pytest.param(_token(_claims(type="refresh")), id="wrong-type"),
        pytest.param(_token(_claims(), secret="x" * 40), id="bad-signature"),
        pytest.param(_token(_claims(sub="nao-uuid")), id="invalid-subject"),
        pytest.param(
            _token({k: v for k, v in _claims().items() if k != "jti"}), id="missing-claim"
        ),
        pytest.param("lixo", id="garbage"),
    ],
)
def test_decode_rejects_invalid_tokens(token: str, settings: Settings) -> None:
    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token, settings)


def test_decode_rejects_alg_none(settings: Settings) -> None:
    token = jwt.encode(_claims(), key=None, algorithm="none")  # type: ignore[arg-type]

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(token, settings)


def test_refresh_tokens_are_random_and_hashed() -> None:
    first, second = new_refresh_token(), new_refresh_token()

    assert first != second
    assert len(first) >= 43
    assert hash_refresh_token(first) == hash_refresh_token(first)
    assert len(hash_refresh_token(first)) == 64
    assert hash_refresh_token(first) != first
