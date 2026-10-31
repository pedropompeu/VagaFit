"""Configuração da aplicação, lida só de variáveis de ambiente (ou `.env` local)."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    return Settings()
