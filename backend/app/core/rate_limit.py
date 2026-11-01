"""Rate limit com slowapi (storage no Redis da aplicação).

A chave é o IP do cliente: o slowapi monta a chave a partir da requisição, antes de o corpo
ser lido. Se o Redis cair, o limite continua valendo em memória do processo.
"""

from collections.abc import Callable
from http import HTTPStatus
from typing import Any, cast

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.errors import error_response

RATE_LIMIT_MESSAGE = "Muitas tentativas. Aguarde um pouco e tente de novo."

_settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=_settings.rate_limit_storage_url or _settings.redis_url,
    enabled=_settings.rate_limit_enabled,
    key_prefix="vagafit",
    in_memory_fallback_enabled=True,
)


def rate_limit[F: Callable[..., Any]](limit: str) -> Callable[[F], F]:
    """Decorator tipado em volta de `limiter.limit`. A rota precisa receber `request: Request`."""
    return cast(Callable[[F], F], limiter.limit(limit, error_message=RATE_LIMIT_MESSAGE))


async def rate_limit_exceeded_handler(_: Request, exc: Exception) -> JSONResponse:
    assert isinstance(exc, RateLimitExceeded)  # noqa: S101 - garantido pelo registro do handler
    limit: Any = exc.limit
    retry_after = int(limit.limit.get_expiry()) if limit is not None else 60
    return error_response(
        HTTPStatus.TOO_MANY_REQUESTS,
        "rate_limited",
        RATE_LIMIT_MESSAGE,
        headers={"Retry-After": str(retry_after)},
    )
