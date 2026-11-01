"""Acesso a `users`.

Exceção à regra de repository com `user_id` no construtor: este repository resolve identidade
(login, cadastro, token), então busca por e-mail ou id. Repositories de recurso (currículos,
vagas, análises, candidaturas) sempre recebem o `user_id` do usuário autenticado.
"""

import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        return await self._session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def add(self, *, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        self._session.add(user)
        await self._session.flush()
        return user

    async def delete(self, user_id: uuid.UUID) -> None:
        """Apaga o usuário. As FKs com `ON DELETE CASCADE` levam o resto junto (LGPD)."""
        await self._session.execute(delete(User).where(User.id == user_id))
