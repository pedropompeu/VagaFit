from httpx import AsyncClient


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
