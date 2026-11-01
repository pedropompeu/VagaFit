import json

import pytest
import structlog

from app.core.config import Settings
from app.core.logging import MAX_FIELD_CHARS, REDACTED, configure_logging, redact_sensitive


def _redact(**fields: object) -> dict[str, object]:
    return dict(redact_sensitive(None, "info", dict(fields)))


@pytest.mark.parametrize(
    "key", ["raw_text", "content", "quote", "answer", "email", "password", "refresh_token"]
)
def test_sensitive_keys_are_replaced(key: str) -> None:
    assert _redact(event="x", **{key: "Python há 5 anos"})[key] == REDACTED


def test_key_match_ignores_case() -> None:
    assert _redact(event="x", Email="ana@exemplo.com")["Email"] == REDACTED


def test_ids_and_short_values_pass_through() -> None:
    event = _redact(
        event="analysis.failed",
        analysis_id="0b6c1a3e-7f1d-4c55-9a51-3f4b8c2d9e10",
        reason="ai_unavailable",
        attempts=2,
    )

    assert event == {
        "event": "analysis.failed",
        "analysis_id": "0b6c1a3e-7f1d-4c55-9a51-3f4b8c2d9e10",
        "reason": "ai_unavailable",
        "attempts": 2,
    }


def test_long_text_in_any_field_is_removed() -> None:
    text = "Experiência com FastAPI e PostgreSQL. " * 20

    redacted = _redact(event="x", detail=text)["detail"]

    assert isinstance(redacted, str)
    assert redacted.startswith(REDACTED)
    assert "FastAPI" not in redacted
    assert len(text) > MAX_FIELD_CHARS


def test_control_fields_are_never_touched() -> None:
    long_event = "e" * (MAX_FIELD_CHARS + 1)
    trace = "Traceback (most recent call last):\n" + "x" * 500

    event = _redact(event=long_event, exception=trace, request_id="abc")

    assert event["event"] == long_event
    assert event["exception"] == trace


def test_configured_pipeline_redacts_before_rendering(capsys: pytest.CaptureFixture[str]) -> None:
    configure_logging(Settings(log_json=True, log_level="INFO"))

    structlog.get_logger("test").info(
        "resume.created", resume_id="r1", raw_text="Ana Exemplo, 8 anos de Python"
    )

    line = capsys.readouterr().out.strip().splitlines()[-1]
    assert "Ana Exemplo" not in line
    assert json.loads(line)["raw_text"] == REDACTED
    assert json.loads(line)["resume_id"] == "r1"
