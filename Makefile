COMPOSE ?= docker compose
TEST_DB_URL = postgresql+asyncpg://$${POSTGRES_USER:-vagafit}:$${POSTGRES_PASSWORD:-vagafit}@db:5432/vagafit_test
BACKEND = $(COMPOSE) run --rm --no-deps api
BACKEND_DB = $(COMPOSE) run --rm api

.PHONY: help up down logs migrate test test-unit lint format seed

help: ## Lista os comandos
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-10s %s\n", $$1, $$2}'

up: ## Sobe api, worker, db, redis e web
	$(COMPOSE) up -d --build

down: ## Derruba os containers (mantém o volume do banco)
	$(COMPOSE) down

logs: ## Acompanha os logs
	$(COMPOSE) logs -f api worker

migrate: ## Aplica as migrações no banco de desenvolvimento
	$(BACKEND_DB) alembic upgrade head

test: ## Testes do backend (com banco de teste e cobertura mínima de 80%)
	$(BACKEND_DB) sh -c 'export DATABASE_URL="$(TEST_DB_URL)" && alembic upgrade head && pytest'

test-unit: ## Só testes que não precisam de banco
	$(BACKEND) pytest -m "not integration" --no-cov

lint: ## ruff + mypy no backend, tsc no frontend
	$(BACKEND) sh -c 'ruff check . && ruff format --check . && mypy app'
	$(COMPOSE) run --rm --no-deps web npm run typecheck

format: ## Formata o backend
	$(BACKEND) sh -c 'ruff check --fix . && ruff format .'

seed: ## Dados de exemplo fictícios (chega na fase 8)
	@echo "seed: ainda não implementado (fase 8)."
