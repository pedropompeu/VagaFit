"""Métricas Prometheus em `/metrics`.

As métricas HTTP (latência, contagem por rota e status) vêm do
prometheus-fastapi-instrumentator. Os contadores de negócio ficam aqui e são
incrementados pelos services. Nenhum rótulo carrega ID, e-mail ou texto: cardinalidade
baixa e nada pessoal.

Cada app tem o próprio `CollectorRegistry`. No registro global, a segunda instância do app
no mesmo processo (os testes criam várias) encontra as métricas HTTP já registradas e o
instrumentator desliga a instrumentação sem avisar. Os contadores de negócio não são
registrados em lugar nenhum na criação; cada app os registra no seu registro.

Com `METRICS_TOKEN` (obrigatório em produção), a rota exige `Authorization: Bearer <token>` e
responde 404 a quem não o tem, como se não existisse: contagem de logins recusados e rotas
mais usadas ajudam quem quer atacar. Sem token, em desenvolvimento, fica aberta.

O worker roda em outro processo e não é exposto aqui; métricas do worker entram quando
houver um exporter próprio (ver `context/achados.md`).
"""

import hmac

from fastapi import Depends, FastAPI, Request
from prometheus_client import (
    GC_COLLECTOR,
    PLATFORM_COLLECTOR,
    PROCESS_COLLECTOR,
    CollectorRegistry,
    Counter,
)
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.config import Settings
from app.core.errors import NotFoundError

METRICS_PATH = "/metrics"

AUTH_LOGIN_FAILURES = Counter(
    "auth_login_failures",
    "Logins recusados (e-mail inexistente ou senha errada).",
    registry=None,
)
AUTH_REFRESH_REUSE_DETECTED = Counter(
    "auth_refresh_reuse_detected",
    "Refresh token já girado que reapareceu; a família inteira foi revogada.",
    registry=None,
)
ANALYSES_REQUESTED = Counter(
    "analyses_requested",
    "Análises pedidas, separadas entre novas e reaproveitadas pelo cache por hash.",
    ["outcome"],
    registry=None,
)
BUSINESS_METRICS = (AUTH_LOGIN_FAILURES, AUTH_REFRESH_REUSE_DETECTED, ANALYSES_REQUESTED)


def _require_token(settings: Settings) -> list[object]:
    if settings.metrics_token is None:
        return []
    expected = f"Bearer {settings.metrics_token.get_secret_value()}".encode()

    def check(request: Request) -> None:
        given = request.headers.get("Authorization", "").encode()
        if not hmac.compare_digest(given, expected):
            raise NotFoundError("Recurso não encontrado.")

    return [Depends(check)]


def instrument(app: FastAPI, settings: Settings) -> CollectorRegistry:
    registry = CollectorRegistry()
    for collector in (*BUSINESS_METRICS, PROCESS_COLLECTOR, PLATFORM_COLLECTOR, GC_COLLECTOR):
        registry.register(collector)
    Instrumentator(
        registry=registry,
        excluded_handlers=[METRICS_PATH, "/health"],
        should_group_status_codes=False,
    ).instrument(app).expose(
        app,
        endpoint=METRICS_PATH,
        include_in_schema=False,
        dependencies=_require_token(settings),
    )
    return registry
