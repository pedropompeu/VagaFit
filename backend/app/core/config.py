"""Configuração da aplicação, lida só de variáveis de ambiente (ou `.env` local)."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Segredo conhecido, aceito só em `local` e `test`. Em produção a aplicação não sobe com ele.
DEV_JWT_SECRET = "dev-only-insecure-jwt-secret-change-me-0000"  # noqa: S105
MIN_JWT_SECRET_BYTES = 32
MIN_METRICS_TOKEN_CHARS = 32


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

    # IA. `fake` é determinístico e não chama API externa: padrão para rodar sem chaves.
    # `gemini` usa o endpoint compatível com OpenAI do Google, pelo mesmo SDK `openai`.
    embedding_provider: Literal["openai", "gemini", "fake"] = "fake"
    llm_provider: Literal["anthropic", "openai", "gemini", "fake"] = "fake"
    openai_api_key: SecretStr | None = None
    anthropic_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None
    openai_embedding_model: str = "text-embedding-3-small"
    openai_llm_model: str = "gpt-4.1-mini"
    anthropic_llm_model: str = "claude-opus-5-5"
    # Versão fixa, não `-latest`: o modelo entra no hash do cache de análise.
    gemini_llm_model: str = "gemini-3.8-flash"
    gemini_embedding_model: str = "gemini-embedding-001"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    llm_max_output_tokens: int = Field(default=16000, gt=0)
    ai_request_timeout_seconds: float = Field(default=60.0, gt=0)
    # LLM com raciocínio pode levar minutos; roda no worker, não na requisição HTTP.
    llm_request_timeout_seconds: float = Field(default=300.0, gt=0)
    # Backoff exponencial em rate limit e falha transitória do provedor.
    ai_max_attempts: int = Field(default=5, ge=1)
    ai_backoff_base_seconds: float = Field(default=1.0, ge=0)
    ai_backoff_max_seconds: float = Field(default=30.0, ge=0)

    # Currículos
    resume_max_upload_bytes: int = Field(default=5 * 1024 * 1024, gt=0)
    resume_max_pdf_pages: int = Field(default=10, gt=0)
    resume_max_text_chars: int = Field(default=50_000, gt=0)
    pdf_extraction_timeout_seconds: float = Field(default=10.0, gt=0)

    # Métricas: com token, `/metrics` exige `Authorization: Bearer <token>`. Obrigatório em
    # produção; sem token (desenvolvimento), a rota fica aberta.
    metrics_token: SecretStr | None = None

    # Tracing de IA (LangFuse). Sem as duas chaves fica desligado, e o código roda igual.
    # Só metadados vão para o LangFuse (tarefa, modelo, tokens, tentativas, erros): nunca
    # texto de currículo, vaga, prompt nem resposta. Ver `app/core/tracing.py`.
    langfuse_public_key: SecretStr | None = None
    langfuse_secret_key: SecretStr | None = None
    langfuse_host: str = "https://cloud.langfuse.com"
    langfuse_sample_rate: float = Field(default=1.0, ge=0, le=1)

    # Análises
    analysis_top_k_chunks: int = Field(default=3, ge=1, le=10)
    # Análise `pending`/`running` mais velha que isto não é reaproveitada (worker caiu).
    analysis_stale_after_minutes: int = Field(default=15, gt=0)

    @model_validator(mode="after")
    def _check_jwt_secret(self) -> "Settings":
        secret = self.jwt_secret.get_secret_value()
        if len(secret.encode()) < MIN_JWT_SECRET_BYTES:
            raise ValueError(f"JWT_SECRET precisa de pelo menos {MIN_JWT_SECRET_BYTES} bytes.")
        if self.environment == "production" and secret == DEV_JWT_SECRET:
            raise ValueError("JWT_SECRET padrão de desenvolvimento não é aceito em produção.")
        return self

    @model_validator(mode="after")
    def _check_metrics_token(self) -> "Settings":
        token = self.metrics_token.get_secret_value() if self.metrics_token else ""
        if self.environment == "production" and not token:
            raise ValueError("METRICS_TOKEN é obrigatório em produção.")
        if token and len(token) < MIN_METRICS_TOKEN_CHARS:
            raise ValueError(
                f"METRICS_TOKEN precisa de pelo menos {MIN_METRICS_TOKEN_CHARS} caracteres."
            )
        return self

    @model_validator(mode="after")
    def _check_ai_providers(self) -> "Settings":
        if self.environment == "production" and "fake" in (
            self.embedding_provider,
            self.llm_provider,
        ):
            raise ValueError("Provedor de IA `fake` não é aceito em produção.")
        if "openai" in (self.embedding_provider, self.llm_provider) and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY é obrigatória com provedor `openai`.")
        if self.llm_provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY é obrigatória com LLM_PROVIDER=anthropic.")
        if "gemini" in (self.embedding_provider, self.llm_provider) and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY é obrigatória com provedor `gemini`.")
        return self

    @model_validator(mode="after")
    def _check_langfuse(self) -> "Settings":
        if bool(self.langfuse_public_key) != bool(self.langfuse_secret_key):
            raise ValueError("LANGFUSE_PUBLIC_KEY e LANGFUSE_SECRET_KEY devem vir juntas.")
        return self

    @property
    def langfuse_enabled(self) -> bool:
        return bool(self.langfuse_public_key) and bool(self.langfuse_secret_key)

    def openai_compatible_endpoint(
        self, provider: Literal["openai", "gemini"]
    ) -> tuple[SecretStr | None, str | None]:
        """Chave e URL base para o SDK `openai`. `None` na URL é a API da própria OpenAI."""
        if provider == "gemini":
            return self.gemini_api_key, self.gemini_base_url
        return self.openai_api_key, None

    @property
    def llm_model_id(self) -> str:
        """Provedor + modelo do LLM. Entra no hash do cache de análise."""
        model = {
            "anthropic": self.anthropic_llm_model,
            "openai": self.openai_llm_model,
            "gemini": self.gemini_llm_model,
            "fake": "fake-llm",
        }[self.llm_provider]
        return f"{self.llm_provider}:{model}"

    @property
    def embedding_model_id(self) -> str:
        model = {
            "openai": self.openai_embedding_model,
            "gemini": self.gemini_embedding_model,
            "fake": "fake",
        }[self.embedding_provider]
        return f"{self.embedding_provider}:{model}"

    @property
    def refresh_cookie_path(self) -> str:
        return f"{self.api_v1_prefix}/auth"

    @property
    def refresh_token_ttl_seconds(self) -> int:
        return self.refresh_token_ttl_days * 24 * 60 * 60


@lru_cache
def get_settings() -> Settings:
    return Settings()
