# VagaFit

Compara uma vaga de emprego com o seu currículo e devolve um score de aderência,
requisito por requisito, **com a evidência tirada do próprio currículo**. O que não tem
evidência aparece como lacuna — o sistema nunca inventa experiência.

> 🚧 Em construção. Fase atual: **0 — setup**. O README completo (demo, arquitetura,
> decisões técnicas, endpoints) chega na fase 8.

## Rodando localmente

Pré-requisitos: Docker com Compose e `make`.

```bash
cp .env.example .env
make up
make migrate
```

- API: http://localhost:8000/docs · health: http://localhost:8000/health
- Front: http://localhost:5173

Portas ocupadas? Ajuste `API_PORT`, `WEB_PORT` e `VITE_API_URL` no `.env`.

## Comandos

| Comando | O que faz |
|---|---|
| `make up` / `make down` | Sobe / derruba api, worker, db, redis e web |
| `make migrate` | Aplica as migrações |
| `make test` | Testes do backend com banco de teste e cobertura mínima de 80% |
| `make test-unit` | Só os testes que não precisam de banco |
| `make lint` | ruff + mypy (strict) + typecheck do front |
| `make format` | Formata o backend |

## Stack

FastAPI · Pydantic v2 · SQLAlchemy 2 async · PostgreSQL 16 + pgvector · Celery + Redis ·
React 18 + Vite + TypeScript. Decisão de arquitetura em
[`docs/adr/ADR-001-stack-e-arquitetura.md`](docs/adr/ADR-001-stack-e-arquitetura.md).
