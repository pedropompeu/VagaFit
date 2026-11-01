"""Provedores de embedding. A aplicação depende só do Protocol `EmbeddingProvider`."""

import hashlib
import math
import re
from typing import Protocol

import openai
import structlog

from app.ai.errors import AIProviderError, RetryableAIError
from app.ai.retry import retry_with_backoff
from app.core.config import Settings
from app.services.text import strip_accents

logger = structlog.get_logger(__name__)

EMBEDDING_DIMENSIONS = 1536
_BATCH_SIZE = 96


class EmbeddingProvider(Protocol):
    model: str

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Um vetor de `EMBEDDING_DIMENSIONS` posições por texto, na mesma ordem."""
        ...

    async def aclose(self) -> None: ...


class OpenAIEmbeddingProvider:
    def __init__(self, settings: Settings, client: openai.AsyncOpenAI | None = None) -> None:
        if client is None:
            if settings.openai_api_key is None:
                raise AIProviderError("Provedor de embedding sem chave configurada.")
            client = openai.AsyncOpenAI(
                api_key=settings.openai_api_key.get_secret_value(),
                max_retries=0,
                timeout=settings.ai_request_timeout_seconds,
            )
        self._client = client
        self._settings = settings
        self.model = settings.openai_embedding_model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for start in range(0, len(texts), _BATCH_SIZE):
            vectors.extend(await self._embed_batch(texts[start : start + _BATCH_SIZE]))
        return vectors

    async def _embed_batch(self, batch: list[str]) -> list[list[float]]:
        async def call() -> list[list[float]]:
            try:
                response = await self._client.embeddings.create(
                    model=self.model, input=batch, dimensions=EMBEDDING_DIMENSIONS
                )
            except (openai.RateLimitError, openai.APIConnectionError) as exc:
                raise RetryableAIError(type(exc).__name__) from exc
            except openai.APIStatusError as exc:
                if exc.status_code >= 500:
                    raise RetryableAIError(f"status {exc.status_code}") from exc
                logger.error("embedding_request_rejected", status=exc.status_code)
                raise AIProviderError() from exc
            ordered = sorted(response.data, key=lambda item: item.index)
            return [list(item.embedding) for item in ordered]

        return await retry_with_backoff(
            call,
            operation="embedding",
            max_attempts=self._settings.ai_max_attempts,
            base_delay=self._settings.ai_backoff_base_seconds,
            max_delay=self._settings.ai_backoff_max_seconds,
        )

    async def aclose(self) -> None:
        await self._client.close()


_WORD = re.compile(r"\w+")


class FakeEmbeddingProvider:
    """Determinístico e sem rede: bag-of-words com hash em 1536 posições, normalizado (L2).

    Textos com palavras em comum ficam próximos, o que basta para testar a busca por
    similaridade sem chamar a OpenAI.
    """

    model = "fake-embedding"

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self.vector(text) for text in texts]

    async def aclose(self) -> None:
        return None

    @staticmethod
    def vector(text: str) -> list[float]:
        values = [0.0] * EMBEDDING_DIMENSIONS
        for word in _WORD.findall(strip_accents(text).casefold()):
            digest = hashlib.blake2b(word.encode(), digest_size=8).digest()
            index = int.from_bytes(digest[:4], "big") % EMBEDDING_DIMENSIONS
            values[index] += 1.0 if digest[4] % 2 == 0 else -1.0
        norm = math.sqrt(sum(v * v for v in values))
        if norm == 0:
            values[0] = 1.0  # texto sem palavras: vetor constante (distância de cosseno definida)
            return values
        return [v / norm for v in values]


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddingProvider(settings)
    return FakeEmbeddingProvider()
