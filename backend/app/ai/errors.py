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
