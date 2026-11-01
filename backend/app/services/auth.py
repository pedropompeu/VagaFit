"""Regras de autenticação: cadastro, login, rotação de refresh, logout e exclusão de conta.

Logs levam só `user_id` e `family_id`. Nunca e-mail, senha ou token (S9).
"""

import uuid
from dataclasses import dataclass
from datetime import timedelta

import structlog
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import ConflictError, ForbiddenError, UnauthorizedError
from app.core.metrics import AUTH_LOGIN_FAILURES, AUTH_REFRESH_REUSE_DETECTED
from app.core.security import (
    AccessToken,
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
    dummy_password_hash,
    hash_password,
    hash_refresh_token,
    new_refresh_token,
    password_needs_rehash,
    verify_password,
)
from app.models.mixins import utcnow
from app.models.user import User
from app.repositories.refresh_tokens import RefreshTokenRepository
from app.repositories.users import UserRepository

logger = structlog.get_logger(__name__)

INVALID_CREDENTIALS = "E-mail ou senha incorretos."
INVALID_SESSION = "Sessão expirada ou inválida. Entre de novo."


@dataclass(frozen=True, slots=True)
class AuthResult:
    user: User
    access: AccessToken
    refresh_token: str


class AuthService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self._session = session
        self._settings = settings
        self._users = UserRepository(session)
        self._tokens = RefreshTokenRepository(session)

    # ------------------------------------------------------------ cadastro e login

    async def register(self, *, email: str, password: str) -> AuthResult:
        if await self._users.get_by_email(email) is not None:
            raise ConflictError("Já existe uma conta com este e-mail.", code="email_taken")
        password_hash = await hash_password(password)
        try:
            user = await self._users.add(email=email, password_hash=password_hash)
        except IntegrityError as exc:  # cadastro simultâneo com o mesmo e-mail
            await self._session.rollback()
            raise ConflictError("Já existe uma conta com este e-mail.", code="email_taken") from exc
        result = await self._open_session(user)
        await self._session.commit()
        logger.info("auth.registered", user_id=str(user.id))
        return result

    async def login(self, *, email: str, password: str) -> AuthResult:
        user = await self._users.get_by_email(email)
        # Com e-mail inexistente, verifica contra um hash fictício: mesmo custo de tempo (S5).
        password_hash = user.password_hash if user is not None else dummy_password_hash()
        valid = await verify_password(password_hash, password)
        if user is None or not valid:
            AUTH_LOGIN_FAILURES.inc()
            logger.info("auth.login_failed", user_id=str(user.id) if user else None)
            raise UnauthorizedError(INVALID_CREDENTIALS, code="invalid_credentials")

        if password_needs_rehash(user.password_hash):
            user.password_hash = await hash_password(password)
        await self._tokens.delete_expired_for_user(user.id, now=utcnow())
        result = await self._open_session(user)
        await self._session.commit()
        logger.info("auth.login", user_id=str(user.id))
        return result

    # ------------------------------------------------------------ refresh e logout

    async def refresh(self, raw_token: str | None) -> AuthResult:
        """Gira o refresh token. Token já girado que reaparece revoga a família inteira."""
        if not raw_token:
            raise UnauthorizedError(INVALID_SESSION, code="invalid_refresh_token")
        now = utcnow()
        current = await self._tokens.get_by_hash_for_update(hash_refresh_token(raw_token))
        if current is None:
            raise UnauthorizedError(INVALID_SESSION, code="invalid_refresh_token")

        if current.revoked_at is not None:
            if current.replaced_by_id is not None:
                await self._tokens.revoke_family(current.family_id, now=now)
                await self._session.commit()
                AUTH_REFRESH_REUSE_DETECTED.inc()
                logger.warning(
                    "auth.refresh_reuse_detected",
                    user_id=str(current.user_id),
                    family_id=str(current.family_id),
                )
            raise UnauthorizedError(INVALID_SESSION, code="invalid_refresh_token")

        if current.expires_at <= now:
            raise UnauthorizedError(INVALID_SESSION, code="invalid_refresh_token")

        user = await self._users.get_by_id(current.user_id)
        if user is None:  # pragma: no cover - a FK em cascata apaga os tokens junto
            raise UnauthorizedError(INVALID_SESSION, code="invalid_refresh_token")

        raw_new = new_refresh_token()
        new = await self._tokens.add(
            user_id=user.id,
            family_id=current.family_id,
            token_hash=hash_refresh_token(raw_new),
            expires_at=now + timedelta(days=self._settings.refresh_token_ttl_days),
        )
        current.revoked_at = now
        current.replaced_by_id = new.id
        await self._session.commit()
        return AuthResult(
            user=user, access=create_access_token(user.id, self._settings), refresh_token=raw_new
        )

    async def logout(self, raw_token: str | None) -> None:
        """Revoga a família do token (encerra esta sessão). Idempotente."""
        if not raw_token:
            return
        current = await self._tokens.get_by_hash_for_update(hash_refresh_token(raw_token))
        if current is None:
            return
        await self._tokens.revoke_family(current.family_id, now=utcnow())
        await self._session.commit()
        logger.info("auth.logout", user_id=str(current.user_id))

    # ------------------------------------------------------------ usuário atual e conta

    async def authenticate(self, access_token: str) -> User:
        try:
            user_id = decode_access_token(access_token, self._settings)
        except InvalidAccessTokenError as exc:
            raise UnauthorizedError("Token inválido ou expirado.", code="invalid_token") from exc
        user = await self._users.get_by_id(user_id)
        if user is None:
            raise UnauthorizedError("Token inválido ou expirado.", code="invalid_token")
        return user

    async def delete_account(self, user: User, *, password: str) -> None:
        """Exclusão definitiva (LGPD). Exige a senha; a cascata apaga tokens e dados."""
        if not await verify_password(user.password_hash, password):
            # 403, não 401: o access token é válido; 401 faria o front tentar refresh.
            raise ForbiddenError("Senha incorreta.", code="invalid_password")
        user_id = user.id
        await self._users.delete(user_id)
        await self._session.commit()
        logger.info("auth.account_deleted", user_id=str(user_id))

    # ------------------------------------------------------------ interno

    async def _open_session(self, user: User) -> AuthResult:
        raw = new_refresh_token()
        await self._tokens.add(
            user_id=user.id,
            family_id=uuid.uuid4(),
            token_hash=hash_refresh_token(raw),
            expires_at=utcnow() + timedelta(days=self._settings.refresh_token_ttl_days),
        )
        return AuthResult(
            user=user, access=create_access_token(user.id, self._settings), refresh_token=raw
        )
