"""Configuração da aplicação, lida só de variáveis de ambiente (ou `.env` local)."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Segredo conhecido, aceito só em `local` e `test`. Em produção a aplicação não sobe com ele.
DEV_JWT_SECRET = "dev-only-insecure-jwt-secret-change-me-0000"  # noqa: S105
MIN_JWT_SECRET_BYTES = 32


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "VagaFit"
    environment: Literal["local", "test", "production"] = "local"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "postgresql+asyncpg://vagafit:vagafit@localhost:5432/vagafit"
    redis_url: str = "redis://localhost:6379/0"

    # Origem exata do front. Com refresh token em cookie, CORS usa credenciais e
    # não aceita curinga.
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_json: bool = True

    health_check_timeout_seconds: float = 2.0

    # Autenticação
    jwt_secret: SecretStr = SecretStr(DEV_JWT_SECRET)
    access_token_ttl_minutes: int = Field(default=15, gt=0)
    refresh_token_ttl_days: int = Field(default=7, gt=0)
    refresh_cookie_name: str = "vagafit_refresh"
    # Navegadores aceitam cookie `Secure` em http://localhost; desligar só se algum não aceitar.
    cookie_secure: bool = True

    # Rate limit (slowapi). Sem URL própria, usa o Redis da aplicação.
    rate_limit_enabled: bool = True
    rate_limit_storage_url: str | None = None

    @model_validator(mode="after")
    def _check_jwt_secret(self) -> "Settings":
        secret = self.jwt_secret.get_secret_value()
        if len(secret.encode()) < MIN_JWT_SECRET_BYTES:
            raise ValueError(f"JWT_SECRET precisa de pelo menos {MIN_JWT_SECRET_BYTES} bytes.")
        if self.environment == "production" and secret == DEV_JWT_SECRET:
            raise ValueError("JWT_SECRET padrão de desenvolvimento não é aceito em produção.")
        return self

    @property
    def refresh_cookie_path(self) -> str:
        return f"{self.api_v1_prefix}/auth"

    @property
    def refresh_token_ttl_seconds(self) -> int:
        return self.refresh_token_ttl_days * 24 * 60 * 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
