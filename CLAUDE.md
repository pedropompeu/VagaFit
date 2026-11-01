# VagaFit — convenções para o Claude Code

Projeto de portfólio: compara uma vaga com o currículo do usuário e devolve aderência por
requisito, sempre com evidência citada do próprio currículo.

Se existir `context/index.md` (memória local da holding, fora do git), leia antes de agir.

## Regra de honestidade (não negociável)

- O sistema nunca inventa experiência, tempo de carreira, tecnologia ou resultado.
- Toda afirmação sobre o candidato cita um chunk do currículo: `chunk_id` + `evidence_quote`.
- O código valida: o chunk existe, pertence ao currículo analisado, e `evidence_quote`
  (normalizada: espaços e caixa) é substring do conteúdo do chunk. Falhou = evidência
  descartada e erro de validação (uma nova tentativa com o erro no prompt, depois `failed`).
- Requisito sem evidência = "não atende" ou "sem evidência". Nunca "atende".
- Triagem sem evidência suficiente = `needs_user_input: true` + a pergunta para o usuário.
- Sugestões de currículo só reorganizam ou reescrevem o que já existe.
- O score é calculado no código (obrigatórios 70%, diferenciais 30%, parcial vale metade;
  se faltar um dos grupos, o outro vale 100%). Nunca pelo LLM.

## Arquitetura

- Monólito modular + worker Celery. Camadas: `api` (routers) → `services` (regra) →
  `repositories` (dados) → `models`. `schemas` para entrada e saída.
- Sessão do banco e usuário autenticado sempre via `Depends` (`app/api/deps.py`).
- Toda query filtra pelo usuário autenticado. Todo recurso novo ganha teste de isolamento
  (usuário B não lê, altera nem apaga dado do usuário A; resposta 404, não 403).
- Nada bloqueante em função `async`: PDF em `run_in_threadpool`; LLM pesado no worker.
- Worker: cada task usa `app.worker.runtime.run_async` (engine próprio em `NullPool`).
  Nunca importe `app.db.session.engine` dentro de task.
- Rotas em `/api/v1`, com `summary` e exemplos no OpenAPI. `/health` fica na raiz.
- Erros: levantar `AppError` (ou subclasse) no service. Formato fixo
  `{"error": {"code": "...", "message": "..."}}`.
- Status de candidatura em código inglês no banco/API (`sent`, `in_review`, `tech_test`,
  `interview`, `offer`, `rejected`, `no_response`); rótulo em português só no front.

## IA

- `LLMProvider` (Anthropic e OpenAI, escolhido por `LLM_PROVIDER`) e `EmbeddingProvider`
  (OpenAI `text-embedding-3-small`, 1536 dims). Fakes determinísticos para teste.
- Nenhum teste chama API externa.
- Saída estruturada validada por Pydantic. Retry com backoff exponencial em rate limit.
- Cache de análise: SHA-256 de (currículo, vaga, modelo, versão do prompt).
- Chunking estrutural: um chunk por experiência (empresa + período + bullets) ou seção
  curta, teto de ~250 tokens, sobreposição só quando um bloco estoura o teto
  (`app/services/chunking.py`, função pura).
- Provedor `fake` é o padrão local e de teste e é recusado em produção. Retry próprio
  (`app/ai/retry.py`) com o retry dos SDKs desligado; falha esgotada vira 503 `ai_unavailable`.
- Citação: use `app.services.text.quote_in_text` (mesma normalização em todo lugar).
- Busca vetorial sempre dentro de um currículo do usuário (`ResumeRepository.nearest_chunks`),
  sem índice ANN de propósito.

## Segurança

- Refresh token em cookie httpOnly `Secure` `SameSite=Strict`; access token só em memória
  no front. CORS com origem exata e credenciais.
- Senha com argon2. Rate limit em login/registro e nos endpoints que chamam LLM.
- Nunca logar texto de currículo ou vaga: só IDs. O processor `redact_sensitive` (structlog) é a
  rede de segurança; não dependa dele. Métricas novas: sem ID, e-mail ou texto em rótulo.
- Upload: até 5 MB, limite de páginas, magic number `%PDF`.
- Segredos só em variável de ambiente. Nunca commitar `.env`, chave ou currículo real.

## Qualidade e fluxo

- `make lint` (ruff + mypy strict + tsc) e `make test` (cobertura mínima de 80%) limpos
  antes de cada commit.
- Um commit por fase, Conventional Commits em inglês, **sem** `Co-Authored-By`.
- Parar no fim de cada fase com resumo do que foi feito e do que revisar.
- Perguntar antes de decisão difícil de desfazer (trocar biblioteca central, mudar modelo
  de dados depois da fase 2).
- Manter este arquivo atualizado com convenções e decisões.

## Fases

0. Setup ✅ · 1. Autenticação ✅ · 2. Currículos ✅ · 3. Vagas ✅ · 4. Worker de análise ✅ ·
5. Triagem ✅ · 6. Candidaturas ✅ · 7. Frontend (exige `BRAND.md`) · 8. Observabilidade,
seed e README (backend ✅; README depois do frontend).
