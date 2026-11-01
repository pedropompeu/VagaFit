"""Acesso a `refresh_tokens`. Mesma exceção de `users`: resolve identidade pelo hash do token."""

import uuid
from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(
        self,
        *,
        user_id: uuid.UUID,
        family_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id, family_id=family_id, token_hash=token_hash, expires_at=expires_at
        )
        self._session.add(token)
        await self._session.flush()
        return token

    async def get_by_hash_for_update(self, token_hash: str) -> RefreshToken | None:
        """Trava a linha: dois refresh simultâneos com o mesmo token não giram os dois."""
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash).with_for_update()
        )
        return result.scalar_one_or_none()

    async def revoke_family(self, family_id: uuid.UUID, *, now: datetime) -> None:
        await self._session.execute(
            update(RefreshToken)
            .where(RefreshToken.family_id == family_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=now)
        )

    async def delete_expired_for_user(self, user_id: uuid.UUID, *, now: datetime) -> None:
        await self._session.execute(
            delete(RefreshToken).where(
                RefreshToken.user_id == user_id, RefreshToken.expires_at < now
            )
        )
