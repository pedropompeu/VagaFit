"""Tracing de IA com LangFuse, só com metadados.

Regra do projeto: nunca sai texto de currículo, vaga, prompt nem resposta. Por isso:

- a API deste módulo não aceita `input` nem `output`: só metadados (IDs, tarefa, modelo,
  versão do prompt, contagens, tokens, tentativa, nome do erro);
- o cliente LangFuse nasce com `mask`, que descarta qualquer string longa que escape;
- só spans do próprio LangFuse são exportados (nenhum instrumentador de SDK entra);
- sem as duas chaves (`LANGFUSE_PUBLIC_KEY` e `LANGFUSE_SECRET_KEY`) tudo vira no-op, e os
  testes nunca ligam o tracing.

Tracing nunca derruba a análise: falha do LangFuse vira log de aviso e a execução segue.
O cliente é criado sob demanda dentro do processo que usa (o worker Celery faz fork).
"""

import threading
from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
from typing import Any, Literal

import structlog

from app.core.config import get_settings

logger = structlog.get_logger(__name__)

# Metadado é ID, nome ou número. Passou disso, é provavelmente texto de usuário.
MAX_METADATA_STRING = 80
REDACTED = "[omitido]"

Level = Literal["DEFAULT", "WARNING", "ERROR"]


def mask_payload(*, data: Any, **_: Any) -> Any:
    """Rede de segurança do cliente LangFuse: mantém números, booleanos e strings curtas."""
    if isinstance(data, str):
        return data if len(data) <= MAX_METADATA_STRING else REDACTED
    if isinstance(data, dict):
        return {str(k): mask_payload(data=v) for k, v in data.items()}
    if isinstance(data, list | tuple):
        return [mask_payload(data=v) for v in data]
    if data is None or isinstance(data, bool | int | float):
        return data
    return REDACTED


class SpanHandle:
    """O que o código de aplicação enxerga de um span. Só aceita metadados."""

    def __init__(self, span: Any | None = None) -> None:
        self._span = span

    def update(
        self,
        *,
        level: Level | None = None,
        status_message: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        **metadata: str | int | float | bool | None,
    ) -> None:
        if self._span is None:
            return
        kwargs: dict[str, Any] = {}
        if metadata:
            kwargs["metadata"] = metadata
        if level is not None:
            kwargs["level"] = level
        if status_message is not None:
            kwargs["status_message"] = status_message
        if input_tokens is not None or output_tokens is not None:
            kwargs["usage_details"] = {
                "input": input_tokens or 0,
                "output": output_tokens or 0,
            }
        if not kwargs:
            return
        try:
            self._span.update(**kwargs)
        except Exception as exc:
            _warn("update", exc)


_NOOP = SpanHandle()
_lock = threading.Lock()
_client: Any | None = None
_initialized = False


def _warn(action: str, exc: Exception) -> None:
    logger.warning("tracing.error", action=action, error=type(exc).__name__)


def _create_client() -> Any | None:
    settings = get_settings()
    public, secret = settings.langfuse_public_key, settings.langfuse_secret_key
    if not (public and secret):
        return None
    try:
        from langfuse import Langfuse, is_langfuse_span

        return Langfuse(
            public_key=public.get_secret_value(),
            secret_key=secret.get_secret_value(),
            host=settings.langfuse_host,
            environment=settings.environment,
            sample_rate=settings.langfuse_sample_rate,
            mask=mask_payload,
            should_export_span=is_langfuse_span,
        )
    except Exception as exc:
        _warn("init", exc)
        return None


def _get_client() -> Any | None:
    """Cliente LangFuse, criado uma vez por processo. `None` com o tracing desligado."""
    global _client, _initialized
    with _lock:
        if not _initialized:
            _client = _create_client()
            _initialized = True
        return _client


def reset_tracing() -> None:
    """Esquece o cliente (testes e reinício de processo)."""
    global _client, _initialized
    with _lock:
        _client = None
        _initialized = False


@contextmanager
def trace_span(
    name: str,
    *,
    generation: bool = False,
    model: str | None = None,
    **metadata: str | int | float | bool | None,
) -> Iterator[SpanHandle]:
    """Abre um span (filho do span atual). Uma geração é uma chamada de LLM."""
    client = _get_client()
    if client is None:
        yield _NOOP
        return
    manager: AbstractContextManager[Any]
    try:
        manager = client.start_as_current_observation(
            name=name,
            as_type="generation" if generation else "span",
            metadata=metadata or None,
            model=model,
        )
        span = manager.__enter__()
    except Exception as exc:
        _warn("start", exc)
        yield _NOOP
        return
    handle = SpanHandle(span)
    try:
        yield handle
    except BaseException as exc:
        # Só o nome da exceção: a mensagem pode carregar texto do usuário.
        handle.update(level="ERROR", status_message=type(exc).__name__)
        _close(manager, exc)
        raise
    _close(manager, None)


def _close(manager: AbstractContextManager[Any], error: BaseException | None) -> None:
    try:
        manager.__exit__(
            type(error) if error else None, error, error.__traceback__ if error else None
        )
    except Exception as exc:
        _warn("end", exc)


def annotate(
    *,
    level: Level | None = None,
    status_message: str | None = None,
    **metadata: str | int | float | bool | None,
) -> None:
    """Atualiza o span atual (por exemplo, o resultado final da análise)."""
    client = _get_client()
    if client is None:
        return
    kwargs: dict[str, Any] = {}
    if metadata:
        kwargs["metadata"] = metadata
    if level is not None:
        kwargs["level"] = level
    if status_message is not None:
        kwargs["status_message"] = status_message
    try:
        client.update_current_span(**kwargs)
    except Exception as exc:
        _warn("annotate", exc)


def record_usage(*, input_tokens: int, output_tokens: int) -> None:
    """Tokens da chamada em andamento, no span de geração atual."""
    client = _get_client()
    if client is None:
        return
    try:
        client.update_current_generation(
            usage_details={"input": input_tokens, "output": output_tokens}
        )
    except Exception as exc:
        _warn("usage", exc)


def flush_tracing() -> None:
    """Envia o que ficou em buffer. Chamar no fim de cada task do worker (processo curto)."""
    client = _client
    if client is None:
        return
    try:
        client.flush()
    except Exception as exc:
        _warn("flush", exc)
