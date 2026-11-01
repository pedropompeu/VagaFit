"""Primitivas de segurança: hash de senha (argon2id), access token (JWT) e refresh token opaco.

- Hash e verificação de senha rodam em thread: argon2 é CPU-bound e travaria o event loop.
- O access token é um JWT HS256 de vida curta, sem estado no servidor.
- O refresh token NÃO é JWT: é um valor aleatório opaco. O banco guarda só o SHA-256 dele.
"""

import hashlib
import secrets
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from functools import cache

import jwt
from anyio import to_thread
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import Settings

JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_TYPE = "access"  # noqa: S105 - nome do tipo, não segredo
_REQUIRED_CLAIMS = ["sub", "type", "exp", "iat", "jti"]

_hasher = PasswordHasher()  # parâmetros padrão do argon2-cffi (argon2id, RFC 9106 low-memory)


class InvalidAccessTokenError(Exception):
    """Token ausente de claims, expirado, adulterado ou de outro tipo."""


# ------------------------------------------------------------------ senha


async def hash_password(password: str) -> str:
    return await to_thread.run_sync(_hasher.hash, password)


async def verify_password(password_hash: str, password: str) -> bool:
    def _verify() -> bool:
        try:
            return _hasher.verify(password_hash, password)
        except (VerificationError, InvalidHashError):
            return False

    return await to_thread.run_sync(_verify)


def password_needs_rehash(password_hash: str) -> bool:
    return _hasher.check_needs_rehash(password_hash)


@cache
def dummy_password_hash() -> str:
    """Hash usado quando o e-mail não existe, para o login levar o mesmo tempo (S5)."""
    return _hasher.hash(secrets.token_urlsafe(16))


# ------------------------------------------------------------------ access token


@dataclass(frozen=True, slots=True)
class AccessToken:
    token: str
    expires_in: int  # segundos


def create_access_token(user_id: uuid.UUID, settings: Settings) -> AccessToken:
    now = datetime.now(UTC)
    ttl = timedelta(minutes=settings.access_token_ttl_minutes)
    payload = {
        "sub": str(user_id),
        "type": ACCESS_TOKEN_TYPE,
        "iat": now,
        "exp": now + ttl,
        "jti": uuid.uuid4().hex,
    }
    token = jwt.encode(payload, settings.jwt_secret.get_secret_value(), algorithm=JWT_ALGORITHM)
    return AccessToken(token=token, expires_in=int(ttl.total_seconds()))


def decode_access_token(token: str, settings: Settings) -> uuid.UUID:
    """Valida assinatura, expiração, claims obrigatórias e tipo. Devolve o id do usuário."""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret.get_secret_value(),
            algorithms=[JWT_ALGORITHM],
            options={"require": _REQUIRED_CLAIMS},
        )
    except jwt.PyJWTError as exc:
        raise InvalidAccessTokenError(type(exc).__name__) from exc
    if payload.get("type") != ACCESS_TOKEN_TYPE:
        raise InvalidAccessTokenError("wrong_token_type")
    try:
        return uuid.UUID(str(payload["sub"]))
    except ValueError as exc:
        raise InvalidAccessTokenError("invalid_subject") from exc


# ------------------------------------------------------------------ refresh token


def new_refresh_token() -> str:
    return secrets.token_urlsafe(32)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
