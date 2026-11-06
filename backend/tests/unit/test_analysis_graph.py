"""Grafo da análise: caminho feliz, nova tentativa com feedback, esgotamento e entrada ausente.

Sem banco: as etapas (`AnalysisSteps`) são stubs e o LLM é o provedor falso com respostas
roteirizadas.
"""

import json
import uuid

import pytest

from app.ai.fake_llm import FakeLLMProvider
from app.ai.llm import MAX_OUTPUT_ATTEMPTS, LLMOutputError
from app.ai.prompts import analyze_fit_request
from app.models.resume import ResumeChunk
from app.schemas.extraction import JobExtraction, Requirement
from app.services.analysis import _Validator, build_result
from app.services.analysis_graph import AnalysisSteps, MissingInputError, build_analysis_graph
from app.services.retrieval import RetrievedContext

CHUNK = "EXPERIÊNCIA\n- Criei APIs REST em FastAPI.\n- Usei PostgreSQL e Redis em produção."

EXTRACTION = JobExtraction(
    title="Backend",
    company=None,
    seniority="mid",
    work_model="remote",
    location=None,
    stack=["FastAPI"],
    requirements=[
        Requirement(id="R1", text="FastAPI", kind="required"),
        Requirement(id="R2", text="Kubernetes", kind="nice_to_have"),
    ],
    model="fake:fake-llm",
    prompt_version="v1",
)

VALID = json.dumps(
    {
        "verdicts": [
            {
                "requirement_id": "R1",
                "verdict": "met",
                "evidence": [{"chunk": "C1", "quote": "Criei APIs REST em FastAPI."}],
                "rationale": "Cita FastAPI.",
            },
            {"requirement_id": "R2", "verdict": "not_met", "evidence": [], "rationale": ""},
        ],
        "suggestions": [],
    }
)
# Cita um trecho que nunca foi enviado: a validação de evidência rejeita.
INVALID = VALID.replace('"chunk": "C1"', '"chunk": "C9"')


def _steps(llm: FakeLLMProvider, *, extraction: JobExtraction | None = EXTRACTION) -> AnalysisSteps:
    ctx = RetrievedContext(
        chunks={"C1": ResumeChunk(id=uuid.uuid4(), content=CHUNK, ordinal=0)},
        candidates={"R1": ["C1"], "R2": ["C1"]},
    )

    async def extract() -> JobExtraction | None:
        return extraction

    async def retrieve(_: JobExtraction) -> RetrievedContext:
        return ctx

    def make_request(e: JobExtraction, c: RetrievedContext):  # type: ignore[no-untyped-def]
        return analyze_fit_request(
            [
                {"id": r.id, "text": r.text, "kind": r.kind, "candidates": c.candidates[r.id]}
                for r in e.requirements
            ],
            {alias: chunk.content for alias, chunk in c.chunks.items()},
        )

    return AnalysisSteps(
        llm=llm,
        extract=extract,
        retrieve=retrieve,
        make_request=make_request,
        validate=lambda e, c, out: _Validator(e, c)(out),
        build=lambda e, c, out: build_result(e, c, out, llm.model),
    )


async def test_happy_path_calls_llm_once_and_builds_result() -> None:
    llm = FakeLLMProvider(scripted=[VALID])

    final = await build_analysis_graph(_steps(llm)).ainvoke({"attempt": 0})

    assert len(llm.requests) == 1
    assert final["attempt"] == 1
    result = final["result"]
    assert [r.verdict for r in result.requirements] == ["met", "not_met"]
    assert result.score == 70  # obrigatório atendido (70%) e diferencial não atendido (0%)


async def test_invalid_output_loops_back_once_with_feedback() -> None:
    llm = FakeLLMProvider(scripted=[INVALID, VALID])

    final = await build_analysis_graph(_steps(llm)).ainvoke({"attempt": 0})

    assert final["attempt"] == 2
    assert len(llm.requests) == 2
    assert llm.requests[0].feedback == ()
    assert any("C9" in p for p in llm.requests[1].feedback)
    assert final["result"].requirements[0].verdict == "met"


async def test_exhausted_attempts_raise_llm_output_error() -> None:
    llm = FakeLLMProvider(scripted=[INVALID] * 5)

    with pytest.raises(LLMOutputError) as exc:
        await build_analysis_graph(_steps(llm)).ainvoke({"attempt": 0})

    assert len(llm.requests) == MAX_OUTPUT_ATTEMPTS
    assert exc.value.task == "analyze_fit"
    assert exc.value.problems


async def test_non_json_output_also_counts_as_an_attempt() -> None:
    llm = FakeLLMProvider(scripted=["não é json", VALID])

    final = await build_analysis_graph(_steps(llm)).ainvoke({"attempt": 0})

    assert final["attempt"] == 2


async def test_missing_job_stops_before_calling_the_llm() -> None:
    llm = FakeLLMProvider(scripted=[VALID])

    with pytest.raises(MissingInputError):
        await build_analysis_graph(_steps(llm, extraction=None)).ainvoke({"attempt": 0})

    assert llm.requests == []


def test_graph_topology_has_the_retry_cycle() -> None:
    graph = build_analysis_graph(_steps(FakeLLMProvider())).get_graph()
    edges = {(e.source, e.target) for e in graph.edges}

    assert ("extract", "retrieve") in edges
    assert ("retrieve", "analyze") in edges
    assert ("analyze", "analyze") in edges  # nova tentativa
    assert ("analyze", "build") in edges
    assert ("analyze", "reject") in edges
