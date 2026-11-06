"""Grafo LangGraph do pipeline de análise.

    extract -> retrieve -> analyze --(validação ok)--------> build -> END
                              ^  \\
                              |   `--(falhou, 1ª vez)--+
                              +--------------------------+  (nova tentativa com o erro no prompt)
                              `--(falhou de novo)-------> reject (LLMOutputError)

O grafo só orquestra. As regras continuam no código de domínio, injetado em `AnalysisSteps`:
recuperação vetorial, validação de evidência, montagem do resultado e score. O estado vive em
memória durante a task: não há checkpointer de propósito, porque o estado carrega trechos do
currículo e a regra do projeto é não persistir esse texto fora do banco da aplicação. A task
é curta e idempotente (a análise tem status e cache por hash), então refazer custa menos
que guardar.

Cada nó vira um span no LangFuse (só metadados). Erros sobem como exceção para o
`AnalysisRunner` traduzir em `failed` com mensagem clara.
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Literal, TypedDict

import structlog
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.ai.llm import (
    MAX_OUTPUT_ATTEMPTS,
    LLMOutputError,
    LLMProvider,
    LLMRequest,
    structured_attempt,
)
from app.core.tracing import trace_span
from app.schemas.analysis import AnalysisResult, LLMAnalysis
from app.schemas.extraction import JobExtraction
from app.services.retrieval import RetrievedContext

logger = structlog.get_logger(__name__)

ANALYZE_TASK = "analyze_fit"


class MissingInputError(Exception):
    """Currículo ou vaga apagados entre o pedido e a execução."""


class AnalysisState(TypedDict, total=False):
    extraction: JobExtraction
    ctx: RetrievedContext
    attempt: int
    problems: list[str]
    output: LLMAnalysis | None
    result: AnalysisResult


@dataclass(frozen=True)
class AnalysisSteps:
    """Dependências do grafo. Em produção vêm do `AnalysisRunner`; nos testes, de stubs."""

    llm: LLMProvider
    extract: Callable[[], Awaitable[JobExtraction | None]]
    retrieve: Callable[[JobExtraction], Awaitable[RetrievedContext]]
    make_request: Callable[[JobExtraction, RetrievedContext], LLMRequest]
    validate: Callable[[JobExtraction, RetrievedContext, LLMAnalysis], list[str]]
    build: Callable[[JobExtraction, RetrievedContext, LLMAnalysis], AnalysisResult]


def build_analysis_graph(
    steps: AnalysisSteps,
) -> CompiledStateGraph[AnalysisState, None, AnalysisState, AnalysisState]:
    async def extract(state: AnalysisState) -> AnalysisState:
        with trace_span("analysis.extract") as span:
            extraction = await steps.extract()
            if extraction is None:
                raise MissingInputError
            span.update(requirements=len(extraction.requirements))
            return {"extraction": extraction}

    async def retrieve(state: AnalysisState) -> AnalysisState:
        with trace_span("analysis.retrieve") as span:
            ctx = await steps.retrieve(state["extraction"])
            span.update(chunks=len(ctx.chunks), items=len(ctx.candidates))
            return {"ctx": ctx}

    async def analyze(state: AnalysisState) -> AnalysisState:
        extraction, ctx = state["extraction"], state["ctx"]
        attempt = state.get("attempt", 0) + 1
        request = steps.make_request(extraction, ctx)
        if attempt > 1:
            request = request.with_feedback(state.get("problems", []))
        with trace_span("analysis.analyze", attempt=attempt) as span:
            output, problems = await structured_attempt(
                steps.llm,
                request,
                LLMAnalysis,
                lambda out: steps.validate(extraction, ctx, out),
                attempt=attempt,
            )
            span.update(valid=output is not None, problems=len(problems))
        if output is None:
            logger.warning(
                "llm_output_rejected", task=ANALYZE_TASK, attempt=attempt, problems=len(problems)
            )
        return {"attempt": attempt, "output": output, "problems": problems}

    def route_after_analyze(state: AnalysisState) -> Literal["build", "analyze", "reject"]:
        if state.get("output") is not None:
            return "build"
        return "analyze" if state["attempt"] < MAX_OUTPUT_ATTEMPTS else "reject"

    async def reject(state: AnalysisState) -> AnalysisState:
        raise LLMOutputError(ANALYZE_TASK, state.get("problems", []))

    async def build(state: AnalysisState) -> AnalysisState:
        output = state["output"]
        if output is None:  # inalcançável: a aresta só leva a `build` com saída válida
            raise LLMOutputError(ANALYZE_TASK, state.get("problems", []))
        with trace_span("analysis.build") as span:
            result = steps.build(state["extraction"], state["ctx"], output)
            span.update(score=result.score, gaps=len(result.gaps))
            return {"result": result}

    graph = StateGraph(AnalysisState)
    graph.add_node("extract", extract)
    graph.add_node("retrieve", retrieve)
    graph.add_node("analyze", analyze)
    graph.add_node("reject", reject)
    graph.add_node("build", build)
    graph.add_edge(START, "extract")
    graph.add_edge("extract", "retrieve")
    graph.add_edge("retrieve", "analyze")
    graph.add_conditional_edges("analyze", route_after_analyze)
    graph.add_edge("build", END)
    graph.add_edge("reject", END)
    return graph.compile()
