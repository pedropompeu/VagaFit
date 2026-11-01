import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.errors import register_exception_handlers
from app.core.metrics import instrument

TOKEN = "t" * 32


async def test_metrics_endpoint_exposes_http_and_business_metrics(client: AsyncClient) -> None:
    await client.get("/api/v1/auth/me")  # 401 sem token, mas conta como tráfego

    response = await client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    body = response.text
    assert "http_requests_total" in body
    assert 'handler="/api/v1/auth/me"' in body
    assert 'status="401"' in body
    for name in (
        "auth_login_failures_total",
        "auth_refresh_reuse_detected_total",
        "analyses_requested_total",
    ):
        assert name in body


async def test_metrics_and_health_are_not_measured_as_traffic(client: AsyncClient) -> None:
    await client.get("/health")
    await client.get("/metrics")

    body = (await client.get("/metrics")).text

    assert 'handler="/metrics"' not in body
    assert 'handler="/health"' not in body


async def test_metrics_is_not_in_the_public_api_schema(client: AsyncClient) -> None:
    schema = (await client.get("/api/v1/openapi.json")).json()

    assert "/metrics" not in schema["paths"]


def test_each_app_instance_is_instrumented() -> None:
    """Regressão: no registro global, a segunda instância ficava sem métricas HTTP."""
    from app.main import create_app

    first, second = create_app(), create_app()

    assert first is not second
    for app in (first, second):
        assert any(getattr(r, "path", None) == "/metrics" for r in app.routes)


async def _get_metrics(settings: Settings, headers: dict[str, str] | None = None) -> int:
    app = FastAPI()
    register_exception_handlers(app)
    instrument(app, settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        return (await client.get("/metrics", headers=headers or {})).status_code


async def test_metrics_with_token_requires_bearer() -> None:
    settings = Settings(metrics_token=TOKEN)  # type: ignore[arg-type]

    assert await _get_metrics(settings, {"Authorization": f"Bearer {TOKEN}"}) == 200


@pytest.mark.parametrize(
    "headers",
    [None, {"Authorization": "Bearer errado"}, {"Authorization": TOKEN}],
)
async def test_metrics_hides_itself_without_the_right_token(
    headers: dict[str, str] | None,
) -> None:
    settings = Settings(metrics_token=TOKEN)  # type: ignore[arg-type]

    assert await _get_metrics(settings, headers) == 404


def test_production_requires_metrics_token() -> None:
    with pytest.raises(ValueError, match="METRICS_TOKEN"):
        Settings(
            environment="production",
            jwt_secret="p" * 40,  # type: ignore[arg-type]
            llm_provider="openai",
            embedding_provider="openai",
            openai_api_key="sk-teste",  # type: ignore[arg-type]
        )


def test_short_metrics_token_is_refused() -> None:
    with pytest.raises(ValueError, match="32 caracteres"):
        Settings(metrics_token="curto")  # type: ignore[arg-type]
