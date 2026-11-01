import math
from types import SimpleNamespace
from typing import Any

import httpx
import openai
import pytest

from app.ai.embeddings import (
    EMBEDDING_DIMENSIONS,
    FakeEmbeddingProvider,
    OpenAIEmbeddingProvider,
    build_embedding_provider,
)
from app.ai.errors import AIProviderError, AIQuotaExceededError
from app.core.config import Settings


def _cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


async def test_fake_is_deterministic_normalized_and_semantic() -> None:
    provider = FakeEmbeddingProvider()
    a, b, c, again = await provider.embed(
        [
            "Experiência com Python e FastAPI",
            "experiencia python fastapi apis",
            "Gestão de pessoas e orçamento",
            "Experiência com Python e FastAPI",
        ]
    )
    assert len(a) == EMBEDDING_DIMENSIONS
    assert math.isclose(math.sqrt(sum(v * v for v in a)), 1.0)
    assert a == again
    assert _cosine(a, b) > _cosine(a, c)


def test_fake_empty_text_has_constant_vector() -> None:
    vector = FakeEmbeddingProvider.vector("  ...  ")
    assert vector[0] == 1.0
    assert sum(vector) == 1.0


def _settings(**overrides: Any) -> Settings:
    base: dict[str, Any] = {
        "embedding_provider": "openai",
        "openai_api_key": "sk-teste",
        "ai_max_attempts": 3,
        "ai_backoff_base_seconds": 0,
        "ai_backoff_max_seconds": 0,
    }
    return Settings(**(base | overrides))


class _FakeEmbeddingsAPI:
    def __init__(self, outcomes: list[Exception | None]) -> None:
        self.outcomes = outcomes
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0) if self.outcomes else None
        if outcome is not None:
            raise outcome
        data = [
            SimpleNamespace(index=i, embedding=[float(i)] * EMBEDDING_DIMENSIONS)
            for i in range(len(kwargs["input"]))
        ]
        return SimpleNamespace(data=list(reversed(data)))


def _client(outcomes: list[Exception | None]) -> tuple[Any, _FakeEmbeddingsAPI]:
    api = _FakeEmbeddingsAPI(outcomes)
    return SimpleNamespace(embeddings=api), api


def _status_error(cls: type[openai.APIStatusError], status: int) -> openai.APIStatusError:
    request = httpx.Request("POST", "https://api.openai.test/v1/embeddings")
    return cls("erro", response=httpx.Response(status, request=request), body=None)


async def test_openai_provider_orders_by_index_and_batches() -> None:
    client, api = _client([])
    provider = OpenAIEmbeddingProvider(_settings(), client=client)

    vectors = await provider.embed([f"texto {i}" for i in range(100)])

    assert len(vectors) == 100
    assert vectors[0][0] == 0.0
    assert vectors[95][0] == 95.0
    assert vectors[96][0] == 0.0  # segundo lote recomeça o índice
    assert [len(c["input"]) for c in api.calls] == [96, 4]
    assert api.calls[0]["dimensions"] == EMBEDDING_DIMENSIONS
    assert api.calls[0]["model"] == "text-embedding-3-small"


class _NoIndexEmbeddingsAPI:
    """Como o endpoint compatível do Gemini: ordem da entrada, `index` vazio."""

    def __init__(self, drop_last: bool = False) -> None:
        self.drop_last = drop_last

    async def create(self, **kwargs: Any) -> Any:
        count = len(kwargs["input"]) - (1 if self.drop_last else 0)
        data = [
            SimpleNamespace(index=None, embedding=[float(i)] * EMBEDDING_DIMENSIONS)
            for i in range(count)
        ]
        return SimpleNamespace(data=data)


async def test_missing_index_keeps_response_order() -> None:
    client = SimpleNamespace(embeddings=_NoIndexEmbeddingsAPI())
    provider = OpenAIEmbeddingProvider(_settings(), client=client)  # type: ignore[arg-type]

    vectors = await provider.embed(["a", "b", "c"])

    assert [v[0] for v in vectors] == [0.0, 1.0, 2.0]


async def test_wrong_vector_count_is_provider_error() -> None:
    client = SimpleNamespace(embeddings=_NoIndexEmbeddingsAPI(drop_last=True))
    provider = OpenAIEmbeddingProvider(_settings(), client=client)  # type: ignore[arg-type]

    with pytest.raises(AIProviderError):
        await provider.embed(["a", "b"])


async def test_openai_provider_retries_rate_limit_and_5xx() -> None:
    client, api = _client(
        [
            _status_error(openai.RateLimitError, 429),
            _status_error(openai.InternalServerError, 500),
            None,
        ]
    )
    provider = OpenAIEmbeddingProvider(_settings(), client=client)

    assert len(await provider.embed(["a"])) == 1
    assert len(api.calls) == 3


async def test_openai_provider_gives_up() -> None:
    request = httpx.Request("POST", "https://api.openai.test")
    client, _ = _client([openai.APIConnectionError(request=request)] * 3)
    provider = OpenAIEmbeddingProvider(_settings(), client=client)

    with pytest.raises(AIProviderError):
        await provider.embed(["a"])


async def test_openai_provider_does_not_retry_4xx() -> None:
    client, api = _client([_status_error(openai.BadRequestError, 400)])
    provider = OpenAIEmbeddingProvider(_settings(), client=client)

    with pytest.raises(AIProviderError):
        await provider.embed(["a"])
    assert len(api.calls) == 1


def test_build_provider() -> None:
    assert isinstance(build_embedding_provider(Settings()), FakeEmbeddingProvider)
    assert isinstance(build_embedding_provider(_settings()), OpenAIEmbeddingProvider)


async def test_gemini_embeddings_use_google_endpoint_and_model() -> None:
    settings = Settings(embedding_provider="gemini", gemini_api_key="gm-teste")  # type: ignore[arg-type]

    provider = build_embedding_provider(settings)

    assert isinstance(provider, OpenAIEmbeddingProvider)
    assert provider.model == "gemini-embedding-001"
    assert str(provider._client.base_url) == settings.gemini_base_url
    await provider.aclose()


async def test_exhausted_quota_is_not_retried() -> None:
    request = httpx.Request("POST", "https://api.openai.test/v1/embeddings")
    body = {"code": "insufficient_quota", "message": "quota", "type": "insufficient_quota"}
    error = openai.RateLimitError(
        "Error code: 429", response=httpx.Response(429, request=request), body=body
    )
    client, api = _client([error, None])
    provider = OpenAIEmbeddingProvider(_settings(), client=client)

    with pytest.raises(AIQuotaExceededError):
        await provider.embed(["a"])
    assert len(api.calls) == 1
