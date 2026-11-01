"""Logs estruturados com structlog e request_id por requisição.

Regra: nunca logar texto de currículo ou de vaga, nem e-mail, senha ou token. Só IDs.
O código já segue a regra; `redact_sensitive` é a rede de segurança caso alguém esqueça.
"""

import logging
import sys
import uuid

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import Settings

REQUEST_ID_HEADER = "X-Request-ID"

REDACTED = "[removido]"
# Campos que carregam texto de currículo, de vaga, de triagem ou credenciais.
SENSITIVE_KEYS = frozenset(
    {
        "text",
        "raw_text",
        "content",
        "resume_text",
        "job_text",
        "quote",
        "evidence",
        "evidence_quote",
        "original",
        "suggestion",
        "question",
        "questions",
        "answer",
        "prompt",
        "system",
        "messages",
        "email",
        "password",
        "token",
        "access_token",
        "refresh_token",
        "authorization",
        "cookie",
    }
)
# Qualquer outro valor de texto mais longo que isto é tratado como conteúdo, não como ID.
MAX_FIELD_CHARS = 200
# Campos de controle do próprio log: nunca mexer.
_PASSTHROUGH_KEYS = frozenset({"event", "level", "timestamp", "request_id", "exception"})


def redact_sensitive(
    _logger: object, _method: str, event_dict: structlog.types.EventDict
) -> structlog.types.EventDict:
    """Processor do structlog: troca campos sensíveis e textos longos por um marcador."""
    for key, value in list(event_dict.items()):
        if key in _PASSTHROUGH_KEYS:
            continue
        if key.lower() in SENSITIVE_KEYS:
            event_dict[key] = REDACTED
        elif isinstance(value, str) and len(value) > MAX_FIELD_CHARS:
            event_dict[key] = f"{REDACTED} ({len(value)} caracteres)"
    return event_dict


def configure_logging(settings: Settings) -> None:
    level = logging.getLevelName(settings.log_level)
    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if settings.log_json
        else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.format_exc_info,
            redact_sensitive,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=False,
    )


class RequestIdMiddleware:
    """Gera (ou reaproveita) um request_id, coloca no contexto dos logs e devolve no header."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        incoming = dict(scope["headers"]).get(REQUEST_ID_HEADER.lower().encode())
        request_id = _sanitize(incoming.decode("latin-1")) if incoming else None
        request_id = request_id or uuid.uuid4().hex

        async def send_with_header(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((REQUEST_ID_HEADER.lower().encode(), request_id.encode()))
                message["headers"] = headers
            await send(message)

        with structlog.contextvars.bound_contextvars(request_id=request_id):
            await self.app(scope, receive, send_with_header)


def _sanitize(value: str) -> str | None:
    """Aceita request_id do cliente só se for curto e alfanumérico (evita log injection)."""
    value = value.strip()
    if 0 < len(value) <= 64 and all(c.isalnum() or c in "-_" for c in value):
        return value
    return None
