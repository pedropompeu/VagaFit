# ADR-001 — Stack e padrão arquitetural

- **Status:** aceito
- **Data:** 2026-10-31

## Contexto

O VagaFit precisa extrair requisitos de vagas, buscar evidências num currículo e pedir
vereditos a um LLM — operações lentas e sujeitas a rate limit — sem travar a API. É um
projeto de uma pessoa, então a operação tem que caber num `docker compose up`.

## Decisão

**Monólito modular em camadas + um worker assíncrono.**

| Camada | Papel |
|---|---|
| `api` | Routers FastAPI: validação de entrada, `Depends`, status HTTP |
| `services` | Regra de negócio: score, validação de evidência, orquestração |
| `repositories` | Acesso a dados; toda query recebe e filtra pelo `user_id` |
| `models` / `schemas` | SQLAlchemy / Pydantic |
| `worker` | Tasks Celery que chamam os mesmos services |

Stack: Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 async + asyncpg, Alembic,
PostgreSQL 16 + pgvector, Celery + Redis 7, React 18 + Vite + TypeScript.

### Worker e SQLAlchemy async

Task Celery é síncrona. Cada task executa `asyncio.run()` com um engine próprio em
`NullPool` (`app/worker/runtime.py`), descartado ao final, e reaproveita os repositories
async da API.

### Embeddings no próprio Postgres

pgvector evita um banco vetorial separado: chunks, currículos e análises ficam no mesmo
banco, com as mesmas FKs e o mesmo filtro por usuário.

## Alternativas descartadas

- **Microsserviços por domínio:** custo operacional sem ganho para uma pessoa; o worker
  já separa o processamento pesado.
- **`BackgroundTasks` do FastAPI:** some se o processo reiniciar; sem retry nem
  visibilidade.
- **arq / Taskiq (filas async nativas):** resolveriam o atrito com asyncio, mas Celery é o
  padrão mais pedido no mercado.
- **Sessão síncrona só no worker:** duplicaria a camada de repositórios.
- **Banco vetorial dedicado (Qdrant, Pinecone):** mais um serviço para um volume de
  dados pequeno.

## Consequências

- Uma imagem Python serve API e worker.
- Toda task abre e fecha conexões (sem pool) — aceitável para tarefas longas e poucas.
- Trocar o modelo de embedding exige migração da coluna `vector(1536)` e reprocessamento.
