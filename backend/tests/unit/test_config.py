import pytest
from pydantic import ValidationError

from app.core.config import DEV_JWT_SECRET, Settings


def test_rejects_short_jwt_secret() -> None:
    with pytest.raises(ValidationError, match="32 bytes"):
        Settings(jwt_secret="curto")  # type: ignore[arg-type]


def test_rejects_dev_secret_in_production() -> None:
    with pytest.raises(ValidationError, match="produção"):
        Settings(environment="production", jwt_secret=DEV_JWT_SECRET)  # type: ignore[arg-type]


def test_accepts_strong_secret_in_production() -> None:
    settings = Settings(
        environment="production",
        jwt_secret="p" * 48,  # type: ignore[arg-type]
        embedding_provider="openai",
        llm_provider="anthropic",
        openai_api_key="sk-teste",  # type: ignore[arg-type]
        anthropic_api_key="sk-ant-teste",  # type: ignore[arg-type]
    )

    assert settings.jwt_secret.get_secret_value() == "p" * 48
    assert "p" * 48 not in repr(settings)


def test_refresh_cookie_is_scoped_to_auth_routes() -> None:
    settings = Settings()

    assert settings.refresh_cookie_path == "/api/v1/auth"
    assert settings.refresh_token_ttl_seconds == 7 * 24 * 60 * 60


def test_rejects_fake_ai_in_production() -> None:
    with pytest.raises(ValidationError, match="fake"):
        Settings(environment="production", jwt_secret="p" * 48)  # type: ignore[arg-type]


def test_requires_openai_key() -> None:
    with pytest.raises(ValidationError, match="OPENAI_API_KEY"):
        Settings(embedding_provider="openai")


def test_requires_anthropic_key() -> None:
    with pytest.raises(ValidationError, match="ANTHROPIC_API_KEY"):
        Settings(llm_provider="anthropic")
