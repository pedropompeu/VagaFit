"""Erros da camada de IA. Viram 503 para o cliente; o detalhe fica só no log."""

from http import HTTPStatus

from app.core.errors import AppError


class AIProviderError(AppError):
    """O provedor falhou depois das tentativas (ou falhou de forma não recuperável)."""

    status_code = HTTPStatus.SERVICE_UNAVAILABLE
    code = "ai_unavailable"

    def __init__(self, message: str = "Serviço de IA indisponível. Tente de novo em instantes."):
        super().__init__(message)


class RetryableAIError(Exception):
    """Falha transitória (rate limit, 5xx, rede). O `retry_with_backoff` tenta de novo."""


class AIQuotaExceededError(AIProviderError):
    """Cota do provedor esgotada (diária ou de crédito). Repetir só gasta tentativa: o pedido
    volta igual até a cota renovar, então falha na hora."""

    code = "ai_quota_exceeded"


_QUOTA_CODES = frozenset({"insufficient_quota"})
_QUOTA_MARKERS = ("exceeded your current quota",)


def is_quota_exhausted(exc: Exception) -> bool:
    """429 de cota esgotada, não de limite por minuto.

    OpenAI manda `code="insufficient_quota"`; o endpoint compatível do Gemini manda o corpo
    numa lista (sem `code`) com a mesma frase. Limite por minuto da OpenAI vem como
    "Rate limit reached" e continua sendo repetido.
    """
    if getattr(exc, "code", None) in _QUOTA_CODES:
        return True
    text = str(exc).lower()
    return any(marker in text for marker in _QUOTA_MARKERS)
