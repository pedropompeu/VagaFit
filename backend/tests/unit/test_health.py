from collections.abc import AsyncIterator
from typing import Any

from fastapi import FastAPI
from httpx import AsyncClient

from app.api.deps import get_cache
from app.db.session import get_session


class FakeSession:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    async def execute(self, *_: Any) -> None:
        if self.fail:
            raise ConnectionError("db down")


class FakeCache:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    async def ping(self) -> bool:
        if self.fail:
            raise ConnectionError("redis down")
        return True


def _override(app: FastAPI, *, db_fail: bool = False, cache_fail: bool = False) -> None:
    async def session() -> AsyncIterator[FakeSession]:
        yield FakeSession(fail=db_fail)

    app.dependency_overrides[get_session] = session
    app.dependency_overrides[get_cache] = lambda: FakeCache(fail=cache_fail)


async def test_health_ok(app: FastAPI, client: AsyncClient) -> None:
    _override(app)

    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": "ok", "redis": "ok"}}


async def test_health_returns_503_when_database_fails(app: FastAPI, client: AsyncClient) -> None:
    _override(app, db_fail=True)

    response = await client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "checks": {"database": "error", "redis": "ok"}}


async def test_health_returns_503_when_redis_fails(app: FastAPI, client: AsyncClient) -> None:
    _override(app, cache_fail=True)

    response = await client.get("/health")

    assert response.status_code == 503
    assert response.json()["checks"]["redis"] == "error"
