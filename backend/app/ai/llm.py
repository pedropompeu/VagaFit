"""Provedores de LLM com saída estruturada. A aplicação depende só de `LLMProvider`.

Cada chamada leva um `LLMRequest` com o prompt e o JSON Schema da resposta. O provedor devolve
o texto JSON; `structured_call` valida com Pydantic e com as regras de domínio (citações),
faz uma nova tentativa com o erro no prompt e, se falhar de novo, levanta `LLMOutputError`.

Nunca logar prompt nem resposta: carregam texto de currículo e de vaga. Só tarefa, modelo,
tokens e duração.
"""

import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any, Literal, Protocol

import anthropic
import openai
import structlog
from pydantic import BaseModel, ValidationError

from app.ai.errors import AIProviderError, RetryableAIError
from app.ai.retry import retry_with_backoff
from app.core.config import Settings

logger = structlog.get_logger(__name__)


class LLMOutputError(Exception):
    """A resposta do LLM não passou na validação nem na segunda tentativa."""

    def __init__(self, task: str, problems: list[str]) -> None:
        super().__init__(f"{task}: {'; '.join(problems)}")
        self.task = task
        self.problems = problems


@dataclass(frozen=True)
class LLMRequest:
    task: str
    system: str
    user: str
    json_schema: dict[str, Any]
    # Dados estruturados que geraram o prompt. Só o provedor fake usa (testes determinísticos).
    payload: Mapping[str, Any] = field(default_factory=dict)
    feedback: tuple[str, ...] = ()

    def with_feedback(self, problems: list[str]) -> "LLMRequest":
        return replace(self, feedback=tuple(problems))

    def user_message(self) -> str:
        if not self.feedback:
            return self.user
        listed = "\n".join(f"- {p}" for p in self.feedback)
        return (
            f"{self.user}\n\n<correcao>\nSua resposta anterior foi rejeitada pela validação:\n"
            f"{listed}\nCorrija e responda de novo seguindo o schema.\n</correcao>"
        )


class LLMProvider(Protocol):
    model: str

    async def complete_json(self, request: LLMRequest) -> str:
        """Texto JSON conforme `request.json_schema`."""
        ...

    async def aclose(self) -> None: ...


def _validation_problems(exc: ValidationError) -> list[str]:
    # Sem `input`: o valor rejeitado pode ser texto do currículo.
    return [
        f"{'.'.join(str(p) for p in err['loc']) or 'raiz'}: {err['msg']}"
        for err in exc.errors(include_input=False, include_url=False)
    ][:10]


async def structured_call[M: BaseModel](
    provider: LLMProvider,
    request: LLMRequest,
    output: type[M],
    validate: Callable[[M], list[str]] | None = None,
) -> M:
    """Chama o LLM, valida e tenta uma segunda vez com o erro no prompt."""
    problems: list[str] = []
    for attempt in (1, 2):
        current = request if attempt == 1 else request.with_feedback(problems)
        raw = await provider.complete_json(current)
        try:
            parsed = output.model_validate_json(raw)
        except ValidationError as exc:
            problems = _validation_problems(exc)
        else:
            problems = validate(parsed) if validate else []
            if not problems:
                return parsed
        logger.warning(
            "llm_output_rejected", task=request.task, attempt=attempt, problems=len(problems)
        )
    raise LLMOutputError(request.task, problems)


class _BaseProvider:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def _with_retry(self, task: str, call: Callable[[], Any]) -> str:
        started = time.perf_counter()
        result: str = await retry_with_backoff(
            call,
            operation=f"llm.{task}",
            max_attempts=self._settings.ai_max_attempts,
            base_delay=self._settings.ai_backoff_base_seconds,
            max_delay=self._settings.ai_backoff_max_seconds,
        )
        logger.info(
            "llm_call",
            task=task,
            model=self.model,  # type: ignore[attr-defined]
            duration_ms=round((time.perf_counter() - started) * 1000),
        )
        return result


class AnthropicLLMProvider(_BaseProvider):
    """Claude com structured outputs (`output_config.format`). Retry do SDK desligado."""

    def __init__(self, settings: Settings, client: anthropic.AsyncAnthropic | None = None) -> None:
        super().__init__(settings)
        if client is None:
            if settings.anthropic_api_key is None:
                raise AIProviderError("Provedor de LLM sem chave configurada.")
            client = anthropic.AsyncAnthropic(
                api_key=settings.anthropic_api_key.get_secret_value(),
                max_retries=0,
                timeout=settings.llm_request_timeout_seconds,
            )
        self._client = client
        self.model = settings.anthropic_llm_model

    async def complete_json(self, request: LLMRequest) -> str:
        async def call() -> str:
            try:
                response = await self._client.messages.create(
                    model=self.model,
                    max_tokens=self._settings.llm_max_output_tokens,
                    system=request.system,
                    messages=[{"role": "user", "content": request.user_message()}],
                    output_config={
                        "format": {"type": "json_schema", "schema": request.json_schema}
                    },
                )
            except (anthropic.RateLimitError, anthropic.APIConnectionError) as exc:
                raise RetryableAIError(type(exc).__name__) from exc
            except anthropic.APIStatusError as exc:
                if exc.status_code >= 500:
                    raise RetryableAIError(f"status {exc.status_code}") from exc
                logger.error("llm_request_rejected", task=request.task, status=exc.status_code)
                raise AIProviderError() from exc
            logger.info(
                "llm_usage",
                task=request.task,
                input_tokens=response.usage.input_tokens,
                output_tokens=response.usage.output_tokens,
                stop_reason=response.stop_reason,
            )
            if response.stop_reason == "refusal":
                raise AIProviderError("O modelo recusou a solicitação.")
            if response.stop_reason == "max_tokens":
                return ""  # JSON truncado: vira erro de validação e uma nova tentativa
            return next((b.text for b in response.content if b.type == "text"), "")

        return await self._with_retry(request.task, call)

    async def aclose(self) -> None:
        await self._client.close()


class OpenAILLMProvider(_BaseProvider):
    """API de chat da OpenAI com `response_format` json_schema estrito. Retry do SDK desligado.

    Com `provider="gemini"`, fala com o endpoint compatível com OpenAI do Google.
    """

    def __init__(
        self,
        settings: Settings,
        client: openai.AsyncOpenAI | None = None,
        *,
        provider: Literal["openai", "gemini"] = "openai",
    ) -> None:
        super().__init__(settings)
        if client is None:
            api_key, base_url = settings.openai_compatible_endpoint(provider)
            if api_key is None:
                raise AIProviderError("Provedor de LLM sem chave configurada.")
            client = openai.AsyncOpenAI(
                api_key=api_key.get_secret_value(),
                base_url=base_url,
                max_retries=0,
                timeout=settings.llm_request_timeout_seconds,
            )
        self._client = client
        self.model = (
            settings.gemini_llm_model if provider == "gemini" else settings.openai_llm_model
        )

    async def complete_json(self, request: LLMRequest) -> str:
        async def call() -> str:
            try:
                response = await self._client.chat.completions.create(
                    model=self.model,
                    max_completion_tokens=self._settings.llm_max_output_tokens,
                    messages=[
                        {"role": "system", "content": request.system},
                        {"role": "user", "content": request.user_message()},
                    ],
                    response_format={
                        "type": "json_schema",
                        "json_schema": {
                            "name": request.task,
                            "schema": request.json_schema,
                            "strict": True,
                        },
                    },
                )
            except (openai.RateLimitError, openai.APIConnectionError) as exc:
                raise RetryableAIError(type(exc).__name__) from exc
            except openai.APIStatusError as exc:
                if exc.status_code >= 500:
                    raise RetryableAIError(f"status {exc.status_code}") from exc
                logger.error("llm_request_rejected", task=request.task, status=exc.status_code)
                raise AIProviderError() from exc
            choice = response.choices[0]
            if choice.message.refusal:
                raise AIProviderError("O modelo recusou a solicitação.")
            return choice.message.content or ""

        return await self._with_retry(request.task, call)

    async def aclose(self) -> None:
        await self._client.close()


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "anthropic":
        return AnthropicLLMProvider(settings)
    if settings.llm_provider in ("openai", "gemini"):
        return OpenAILLMProvider(settings, provider=settings.llm_provider)
    from app.ai.fake_llm import FakeLLMProvider

    return FakeLLMProvider()
