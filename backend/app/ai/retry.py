"""Retry com backoff exponencial e jitter para chamadas a provedores de IA.

Os SDKs têm retry próprio, mas ele fica desligado (`max_retries=0`): aqui o número de
tentativas e o tempo de espera são configuráveis e testáveis (o `sleep` é injetável).
"""

import asyncio
import random
from collections.abc import Awaitable, Callable

import structlog

from app.ai.errors import AIProviderError, RetryableAIError

logger = structlog.get_logger(__name__)

Sleep = Callable[[float], Awaitable[None]]


def backoff_delay(attempt: int, *, base: float, maximum: float, jitter: float) -> float:
    """Espera antes da tentativa `attempt + 1` (attempt começa em 1). `jitter` em [0, 1)."""
    delay: float = min(maximum, base * (2 ** (attempt - 1)))
    return delay * (0.5 + jitter / 2)


async def retry_with_backoff[T](
    call: Callable[[], Awaitable[T]],
    *,
    operation: str,
    max_attempts: int,
    base_delay: float,
    max_delay: float,
    sleep: Sleep = asyncio.sleep,
    rand: Callable[[], float] = random.random,
) -> T:
    """Executa `call`; em `RetryableAIError` espera e tenta de novo até `max_attempts`."""
    for attempt in range(1, max_attempts + 1):
        try:
            return await call()
        except RetryableAIError as exc:
            if attempt == max_attempts:
                logger.warning("ai_retry_exhausted", operation=operation, attempts=attempt)
                raise AIProviderError() from exc
            delay = backoff_delay(attempt, base=base_delay, maximum=max_delay, jitter=rand())
            logger.info(
                "ai_retry", operation=operation, attempt=attempt, delay_seconds=round(delay, 2)
            )
            await sleep(delay)
    raise AssertionError("inalcançável")  # pragma: no cover
