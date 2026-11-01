"""Fixtures com banco real. Cada teste roda numa transação desfeita no final."""

import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import build_engine, get_session

PASSWORD = "senha-de-teste-123"


@pytest.fixture
async def db_session() -> AsyncIterator[AsyncSession]:
    engine = build_engine(get_settings().database_url, null_pool=True)
    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()
    await engine.dispose()


@pytest.fixture
def app(app: FastAPI, db_session: AsyncSession) -> FastAPI:
    async def _session() -> AsyncIterator[AsyncSession]:
        yield db_session

    app.dependency_overrides[get_session] = _session
    return app


@dataclass(frozen=True)
class AuthedUser:
    id: uuid.UUID
    email: str
    password: str
    access_token: str

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}


async def register(client: AsyncClient, email: str, password: str = PASSWORD) -> AuthedUser:
    response = await client.post(
        "/api/v1/auth/register", json={"email": email, "password": password}
    )
    assert response.status_code == 201, response.text
    body = response.json()
    return AuthedUser(
        id=uuid.UUID(body["user"]["id"]),
        email=email,
        password=password,
        access_token=body["access_token"],
    )


@pytest.fixture
async def user_a(client: AsyncClient) -> AuthedUser:
    """Dono dos dados nos testes de isolamento."""
    return await register(client, "ana@exemplo.com")


@pytest.fixture
async def user_b(client: AsyncClient) -> AuthedUser:
    """Outro usuário: nunca pode ler, alterar ou apagar dado de `user_a` (espera 404)."""
    return await register(client, "bruno@exemplo.com")
