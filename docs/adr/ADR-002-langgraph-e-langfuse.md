# ADR-002 — LangGraph na orquestração da análise e LangFuse nos traces

- **Status:** aceito
- **Data:** 2026-11-06

## Contexto

O pipeline de análise tinha quatro etapas encadeadas à mão dentro do `AnalysisRunner`
(extrair a vaga, recuperar trechos, pedir o veredito ao LLM, montar o resultado) e uma nova
tentativa escondida dentro de `structured_call`. Funcionava, mas:

- o ciclo de nova tentativa não era visível nem testável como parte do fluxo;
- não havia como saber, por análise, quantas tentativas, quantos tokens e quanto tempo cada
  etapa levou. Os logs estruturados e o Prometheus respondem "quantas", não "onde demorou".

## Decisão

**LangGraph só como orquestrador.** O `AnalysisRunner` monta um `StateGraph`
(`app/services/analysis_graph.py`):

```
extract -> retrieve -> analyze --ok--> build -> END
                         ^  \
                         |   `--falhou (1ª vez)--+
                         +-----------------------+   volta com o erro no prompt
                         `--falhou de novo--> reject (LLMOutputError)
```

As regras continuam em código de domínio, injetado em `AnalysisSteps`: busca vetorial,
validação de evidência (citação literal), score e lacunas. O grafo não decide nada de negócio.
Continuam valendo `LLMProvider`, `EmbeddingProvider`, o retry com backoff e a validação
Pydantic. **Não usamos LangChain**: os nós chamam os provedores do projeto.

`structured_call` virou um laço sobre `structured_attempt` (uma chamada + validação). O grafo
usa a mesma peça como nó, então extração e triagem seguem com o comportamento de antes.

**LangFuse só com metadados** (`app/core/tracing.py`). Cada análise é um trace: um span raiz
(`analysis.run`), um span por nó e uma geração por chamada de LLM, com tarefa, modelo, versão
do prompt, tentativa, contagens, tokens, status e nome do erro. A API do módulo não aceita
`input` nem `output`, o cliente nasce com `mask` que descarta strings longas, e só spans do
LangFuse são exportados. Sem `LANGFUSE_PUBLIC_KEY` e `LANGFUSE_SECRET_KEY`, tudo é no-op, e os
testes nunca ligam o tracing. Falha do LangFuse vira aviso no log e a análise segue.

### Sem checkpointer, de propósito

O estado do grafo carrega trechos do currículo. Persisti-lo (Postgres saver, Redis) criaria
uma segunda cópia de texto pessoal fora das tabelas que já têm isolamento por usuário e
política de apagamento. A task é curta e idempotente (a análise tem status e cache por hash),
então refazer custa menos que guardar.

## Alternativas descartadas

- **Manter o encadeamento manual:** simples, mas o ciclo de nova tentativa continua implícito
  e a observabilidade por etapa exigiria o mesmo código de span espalhado à mão.
- **LangChain + callback do LangFuse:** trocaria a biblioteca central de LLM do projeto
  (decisão difícil de desfazer) só para ganhar o tracing automático.
- **Traces com prompt e resposta:** ajudam a depurar, mas contrariam a regra de nunca sair
  texto de currículo ou vaga do servidor. Fica para um modo de desenvolvimento, se for preciso.
- **LangFuse self-hosted:** a versão atual exige vários serviços (ClickHouse, Redis, storage)
  e pesa o `docker compose` de um projeto de uma pessoa. Usamos o plano gratuito da nuvem.

## Consequências

- Duas dependências novas no backend: `langgraph` e `langfuse`.
- O custo de cada etapa e de cada nova tentativa passa a ser visível por análise.
- A triagem continua sem grafo: é uma única chamada síncrona, e um grafo de um nó só seria
  cerimônia. Vale revisitar se ela ganhar passos (por exemplo, perguntar ao usuário).
- Ainda não há eval harness. O LangFuse mede custo e latência, não qualidade; o próximo passo
  é um golden set com datasets e scores do LangFuse.
