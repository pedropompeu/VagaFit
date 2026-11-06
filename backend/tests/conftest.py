import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("LOG_JSON", "false")
# Rate limit em memória nos testes (o CI não tem Redis); ligado só nos testes de limite.
os.environ.setdefault("RATE_LIMIT_STORAGE_URL", "memory://")
# Provedores falsos sempre: nenhum teste chama API externa, mesmo com chave no `.env`.
os.environ["EMBEDDING_PROVIDER"] = "fake"
os.environ["LLM_PROVIDER"] = "fake"
# Chaves e ajustes de provedor do `.env` (modelo, URL) e do LangFuse (tracing sempre desligado
# nos testes) também ficam de fora: os testes
# esperam os padrões do código, e os de validação dependem da ausência da chave.
for _name in [
    n for n in os.environ if n.startswith(("OPENAI_", "ANTHROPIC_", "GEMINI_", "LANGFUSE_"))
]:
    del os.environ[_name]

from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_task_queue
from app.core.rate_limit import limiter
from app.main import create_app
from app.worker.queue import InMemoryTaskQueue


@pytest.fixture(autouse=True)
def _rate_limit_off() -> Iterator[None]:
    limiter.reset()
    limiter.enabled = False
    yield
    limiter.enabled = False


@pytest.fixture
def rate_limited() -> None:
    """Liga o rate limit (zerado) no teste que pedir esta fixture."""
    limiter.reset()
    limiter.enabled = True


@pytest.fixture
def task_queue() -> InMemoryTaskQueue:
    """Fila em memória: o teste confere o que seria enfileirado sem Redis nem worker."""
    return InMemoryTaskQueue()


@pytest.fixture
def app(task_queue: InMemoryTaskQueue) -> FastAPI:
    application = create_app()
    application.dependency_overrides[get_task_queue] = lambda: task_queue
    return application


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    # https: o cookie de refresh é `Secure` e o httpx só o devolve em https.
    async with AsyncClient(transport=transport, base_url="https://test") as ac:
        yield ac
