import json
from types import SimpleNamespace
from typing import Any

import anthropic
import httpx2
import openai
import pytest
from pydantic import BaseModel, Field

from app.ai.errors import AIProviderError
from app.ai.fake_llm import FakeLLMProvider
from app.ai.llm import (
    AnthropicLLMProvider,
    LLMOutputError,
    LLMRequest,
    OpenAILLMProvider,
    build_llm_provider,
    structured_call,
)
from app.core.config import Settings


class Answer(BaseModel):
    value: int = Field(ge=0)


def _request(**overrides: Any) -> LLMRequest:
    base: dict[str, Any] = {
        "task": "answer",
        "system": "sistema",
        "user": "pergunta",
        "json_schema": {"type": "object"},
    }
    return LLMRequest(**(base | overrides))


async def test_structured_call_retries_with_feedback_after_invalid_json() -> None:
    llm = FakeLLMProvider(scripted=["não é json", '{"value": 3}'])

    result = await structured_call(llm, _request(), Answer)

    assert result.value == 3
    assert len(llm.requests) == 2
    assert "<correcao>" not in llm.requests[0].user_message()
    second = llm.requests[1].user_message()
    assert second.startswith("pergunta")
    assert "<correcao>" in second


async def test_structured_call_runs_domain_validation() -> None:
    llm = FakeLLMProvider(scripted=['{"value": 1}', '{"value": 2}'])

    def even(answer: Answer) -> list[str]:
        return [] if answer.value % 2 == 0 else ["value: precisa ser par"]

    result = await structured_call(llm, _request(), Answer, even)

    assert result.value == 2
    assert "value: precisa ser par" in llm.requests[1].user_message()


async def test_structured_call_gives_up_after_second_failure() -> None:
    llm = FakeLLMProvider(scripted=['{"value": -1}', "{}"])

    with pytest.raises(LLMOutputError) as info:
        await structured_call(llm, _request(), Answer)

    assert info.value.task == "answer"
    assert info.value.problems
    assert len(llm.requests) == 2


async def test_validation_feedback_never_echoes_the_rejected_value() -> None:
    llm = FakeLLMProvider(scripted=['{"value": "SEGREDO-DO-CV"}', '{"value": 1}'])

    await structured_call(llm, _request(), Answer)

    assert "SEGREDO-DO-CV" not in llm.requests[1].user_message()


def _settings(**overrides: Any) -> Settings:
    base: dict[str, Any] = {
        "llm_provider": "anthropic",
        "anthropic_api_key": "sk-ant-teste",
        "openai_api_key": "sk-teste",
        "ai_max_attempts": 3,
        "ai_backoff_base_seconds": 0,
        "ai_backoff_max_seconds": 0,
    }
    return Settings(**(base | overrides))


class _Calls:
    def __init__(self, outcomes: list[Any]) -> None:
        self.outcomes = outcomes
        self.calls: list[dict[str, Any]] = []

    async def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def _anthropic_response(text: str, stop_reason: str = "end_turn") -> Any:
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)],
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=10, output_tokens=5),
    )


def _anthropic_status(cls: type[anthropic.APIStatusError], status: int) -> Exception:
    request = httpx2.Request("POST", "https://api.anthropic.test/v1/messages")
    return cls("erro", response=httpx2.Response(status, request=request), body=None)


def _anthropic(outcomes: list[Any]) -> tuple[AnthropicLLMProvider, _Calls]:
    calls = _Calls(outcomes)
    client: Any = SimpleNamespace(messages=calls)
    return AnthropicLLMProvider(_settings(), client=client), calls


async def test_anthropic_sends_schema_and_returns_text() -> None:
    provider, calls = _anthropic([_anthropic_response('{"value": 1}')])

    raw = await provider.complete_json(_request(json_schema={"type": "object", "x": 1}))

    assert json.loads(raw) == {"value": 1}
    sent = calls.calls[0]
    assert sent["model"] == provider.model
    assert sent["system"] == "sistema"
    assert sent["output_config"]["format"] == {
        "type": "json_schema",
        "schema": {"type": "object", "x": 1},
    }
    assert "temperature" not in sent


async def test_anthropic_retries_rate_limit_and_server_errors() -> None:
    provider, calls = _anthropic(
        [
            _anthropic_status(anthropic.RateLimitError, 429),
            _anthropic_status(anthropic.InternalServerError, 500),
            _anthropic_response('{"value": 2}'),
        ]
    )

    assert json.loads(await provider.complete_json(_request())) == {"value": 2}
    assert len(calls.calls) == 3


async def test_anthropic_connection_error_is_retried_then_gives_503() -> None:
    request = httpx2.Request("POST", "https://api.anthropic.test/v1/messages")
    provider, calls = _anthropic([anthropic.APIConnectionError(request=request) for _ in range(3)])

    with pytest.raises(AIProviderError):
        await provider.complete_json(_request())
    assert len(calls.calls) == 3


async def test_anthropic_client_error_is_not_retried() -> None:
    provider, calls = _anthropic([_anthropic_status(anthropic.BadRequestError, 400)])

    with pytest.raises(AIProviderError):
        await provider.complete_json(_request())
    assert len(calls.calls) == 1


async def test_anthropic_refusal_is_provider_error() -> None:
    provider, _ = _anthropic([_anthropic_response("", stop_reason="refusal")])

    with pytest.raises(AIProviderError):
        await provider.complete_json(_request())


async def test_anthropic_truncated_output_becomes_retry_in_structured_call() -> None:
    provider, calls = _anthropic(
        [
            _anthropic_response('{"value": ', stop_reason="max_tokens"),
            _anthropic_response('{"value": 4}'),
        ]
    )

    result = await structured_call(provider, _request(), Answer)

    assert result.value == 4
    assert "<correcao>" in calls.calls[1]["messages"][0]["content"]


def _openai_response(content: str | None, refusal: str | None = None) -> Any:
    message = SimpleNamespace(content=content, refusal=refusal)
    return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def _openai(outcomes: list[Any]) -> tuple[OpenAILLMProvider, _Calls]:
    calls = _Calls(outcomes)
    client: Any = SimpleNamespace(chat=SimpleNamespace(completions=calls))
    return OpenAILLMProvider(_settings(llm_provider="openai"), client=client), calls


def _openai_status(cls: type[openai.APIStatusError], status: int) -> Exception:
    import httpx

    request = httpx.Request("POST", "https://api.openai.test/v1/chat/completions")
    return cls("erro", response=httpx.Response(status, request=request), body=None)


async def test_openai_uses_strict_json_schema_and_retries() -> None:
    provider, calls = _openai(
        [_openai_status(openai.RateLimitError, 429), _openai_response('{"value": 5}')]
    )

    raw = await provider.complete_json(_request())

    assert json.loads(raw) == {"value": 5}
    sent = calls.calls[1]
    assert sent["response_format"]["json_schema"]["strict"] is True
    assert sent["messages"][0] == {"role": "system", "content": "sistema"}


async def test_openai_refusal_and_client_error() -> None:
    provider, _ = _openai([_openai_response(None, refusal="não")])
    with pytest.raises(AIProviderError):
        await provider.complete_json(_request())

    provider, calls = _openai([_openai_status(openai.AuthenticationError, 401)])
    with pytest.raises(AIProviderError):
        await provider.complete_json(_request())
    assert len(calls.calls) == 1


def test_build_llm_provider_by_setting() -> None:
    assert isinstance(build_llm_provider(_settings()), AnthropicLLMProvider)
    assert isinstance(build_llm_provider(_settings(llm_provider="openai")), OpenAILLMProvider)
    assert isinstance(build_llm_provider(Settings(llm_provider="fake")), FakeLLMProvider)


async def test_gemini_llm_uses_google_endpoint_and_model() -> None:
    settings = Settings(llm_provider="gemini", gemini_api_key="gm-teste")  # type: ignore[arg-type]

    provider = build_llm_provider(settings)

    assert isinstance(provider, OpenAILLMProvider)
    assert provider.model == "gemini-3.8-flash"
    assert str(provider._client.base_url) == settings.gemini_base_url
    await provider.aclose()
