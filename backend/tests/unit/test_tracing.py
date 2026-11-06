"""Tracing: no-op sem chaves, só metadados, nunca vaza texto e nunca derruba a análise."""

from collections.abc import Iterator
from typing import Any

import pytest
from pydantic import ValidationError

from app.core import tracing
from app.core.config import Settings
from app.core.tracing import REDACTED, mask_payload, trace_span


class _Span:
    def __init__(self) -> None:
        self.updates: list[dict[str, Any]] = []

    def update(self, **kwargs: Any) -> None:
        self.updates.append(kwargs)


class _Manager:
    def __init__(self, span: _Span, log: list[Any]) -> None:
        self._span = span
        self._log = log

    def __enter__(self) -> _Span:
        return self._span

    def __exit__(self, *exc_info: Any) -> None:
        self._log.append(exc_info[0])


class _Client:
    def __init__(self) -> None:
        self.started: list[dict[str, Any]] = []
        self.span = _Span()
        self.exits: list[Any] = []
        self.current_updates: list[dict[str, Any]] = []
        self.flushed = 0

    def start_as_current_observation(self, **kwargs: Any) -> _Manager:
        self.started.append(kwargs)
        return _Manager(self.span, self.exits)

    def update_current_span(self, **kwargs: Any) -> None:
        self.current_updates.append(kwargs)

    def update_current_generation(self, **kwargs: Any) -> None:
        self.current_updates.append(kwargs)

    def flush(self) -> None:
        self.flushed += 1


@pytest.fixture
def client() -> Iterator[_Client]:
    fake = _Client()
    tracing._client, tracing._initialized = fake, True
    yield fake
    tracing.reset_tracing()


@pytest.fixture(autouse=True)
def _reset() -> Iterator[None]:
    tracing.reset_tracing()
    yield
    tracing.reset_tracing()


def test_mask_keeps_numbers_and_short_strings_and_redacts_long_text() -> None:
    long_text = "Criei APIs REST em FastAPI e PostgreSQL para um banco digital. " * 3

    masked = mask_payload(
        data={"id": "abc", "n": 3, "ok": True, "texto": long_text, "l": [long_text]}
    )

    assert masked == {"id": "abc", "n": 3, "ok": True, "texto": REDACTED, "l": [REDACTED]}


def test_mask_redacts_unknown_objects() -> None:
    assert mask_payload(data=object()) == REDACTED


def test_disabled_tracing_is_a_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)

    with trace_span("analysis.run", analysis_id="x") as span:
        span.update(status="done", input_tokens=1)

    tracing.annotate(reason="x")
    tracing.record_usage(input_tokens=1, output_tokens=2)
    tracing.flush_tracing()


def test_span_receives_only_metadata(client: _Client) -> None:
    with trace_span("llm.analyze_fit", generation=True, model="m", attempt=1) as span:
        span.update(valid=True, input_tokens=10, output_tokens=5)

    started = client.started[0]
    assert started["as_type"] == "generation"
    assert started["model"] == "m"
    assert started["metadata"] == {"attempt": 1}
    assert "input" not in started
    assert "output" not in started
    assert client.span.updates == [
        {"metadata": {"valid": True}, "usage_details": {"input": 10, "output": 5}}
    ]


def test_error_records_only_the_exception_name_and_propagates(client: _Client) -> None:
    def run() -> None:
        with trace_span("analysis.build"):
            raise ValueError("segredo do currículo")

    with pytest.raises(ValueError, match="segredo"):
        run()

    assert client.span.updates == [{"level": "ERROR", "status_message": "ValueError"}]
    assert client.exits == [ValueError]
    assert "segredo" not in repr(client.span.updates)


def test_tracing_failure_never_breaks_the_caller(client: _Client) -> None:
    def boom(**_: Any) -> None:
        raise RuntimeError("langfuse fora do ar")

    client.start_as_current_observation = boom  # type: ignore[method-assign]
    client.update_current_span = boom  # type: ignore[method-assign]
    client.flush = boom  # type: ignore[method-assign]

    with trace_span("analysis.run") as span:
        span.update(status="done")
    tracing.annotate(reason="x")
    tracing.flush_tracing()


def test_annotate_and_usage_update_the_current_observation(client: _Client) -> None:
    tracing.annotate(level="ERROR", status_message="ai_unavailable", reason="ai_unavailable")
    tracing.record_usage(input_tokens=7, output_tokens=3)
    tracing.flush_tracing()

    assert client.current_updates[0] == {
        "metadata": {"reason": "ai_unavailable"},
        "level": "ERROR",
        "status_message": "ai_unavailable",
    }
    assert client.current_updates[1] == {"usage_details": {"input": 7, "output": 3}}
    assert client.flushed == 1


def test_langfuse_keys_must_come_together() -> None:
    with pytest.raises(ValidationError, match="LANGFUSE_PUBLIC_KEY"):
        Settings(_env_file=None, langfuse_public_key="pk-lf-1")  # type: ignore[arg-type]


def test_langfuse_enabled_only_with_both_keys() -> None:
    off = Settings(_env_file=None)
    on = Settings(_env_file=None, langfuse_public_key="pk", langfuse_secret_key="sk")  # type: ignore[arg-type]

    assert not off.langfuse_enabled
    assert on.langfuse_enabled
