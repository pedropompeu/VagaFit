import pytest
from httpx import AsyncClient

from app.core.config import Settings
from app.core.logging import configure_logging
from app.worker.runtime import run_async
from app.worker.tasks import ping


async def test_openapi_is_versioned(client: AsyncClient) -> None:
    response = await client.get("/api/v1/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"]["title"] == "VagaFit API"


async def test_cors_allows_only_configured_origin(client: AsyncClient) -> None:
    allowed = await client.options(
        "/health",
        headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
    )
    denied = await client.options(
        "/health",
        headers={"Origin": "http://evil.example", "Access-Control-Request-Method": "GET"},
    )

    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert allowed.headers["access-control-allow-credentials"] == "true"
    assert "access-control-allow-origin" not in denied.headers


def test_settings_read_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORS_ORIGINS", '["https://vagafit.example"]')
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    settings = Settings()

    assert settings.cors_origins == ["https://vagafit.example"]
    assert settings.log_level == "DEBUG"


def test_configure_logging_supports_json_and_console() -> None:
    configure_logging(Settings(log_json=True))
    configure_logging(Settings(log_json=False))


def test_ping_task_runs_eagerly() -> None:
    assert ping.apply().get() == "pong"


def test_run_async_executes_job_and_returns_value() -> None:
    received: list[object] = []

    async def job(session: object) -> str:
        received.append(session)
        return "done"

    # Sessão é criada sem conectar; o job não toca no banco.
    result = run_async(job, database_url="postgresql+asyncpg://u:p@localhost:1/none")

    assert result == "done"
    assert len(received) == 1
