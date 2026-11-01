"""Validação da saída do LLM na análise: citação literal, só trechos enviados, todos os IDs."""

import uuid

from app.models.resume import ResumeChunk
from app.schemas.analysis import LLMAnalysis
from app.schemas.extraction import JobExtraction, Requirement
from app.services.analysis import RetrievedContext, _Validator, build_result

CHUNK = "EXPERIÊNCIA\n- Criei APIs REST em FastAPI.\n- Usei PostgreSQL e Redis em produção."

EXTRACTION = JobExtraction(
    title="Backend",
    company=None,
    seniority="mid",
    work_model="remote",
    location=None,
    stack=["FastAPI", "PostgreSQL"],
    requirements=[
        Requirement(id="R1", text="FastAPI", kind="required"),
        Requirement(id="R2", text="Kubernetes", kind="nice_to_have"),
    ],
    model="fake:fake-llm",
    prompt_version="v1",
)


def _ctx() -> RetrievedContext:
    chunk = ResumeChunk(id=uuid.uuid4(), content=CHUNK, ordinal=0)
    return RetrievedContext(chunks={"C1": chunk}, candidates={"R1": ["C1"], "R2": ["C1"]})


def _out(**overrides: object) -> LLMAnalysis:
    data: dict = {
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
    data.update(overrides)
    return LLMAnalysis.model_validate(data)


def test_valid_output_has_no_problems() -> None:
    assert _Validator(EXTRACTION, _ctx())(_out()) == []


def test_quote_must_be_literal() -> None:
    out = _out()
    out.verdicts[0].evidence[0].quote = "Liderei time de 10 pessoas com FastAPI."
    problems = _Validator(EXTRACTION, _ctx())(out)
    assert problems == ["verdicts.0 (R1).evidence.0: a citação não é cópia literal do trecho C1"]


def test_quote_matches_ignoring_case_and_spacing() -> None:
    out = _out()
    out.verdicts[0].evidence[0].quote = "usei  postgresql e REDIS\nem produção"
    assert _Validator(EXTRACTION, _ctx())(out) == []


def test_alias_not_sent_is_rejected() -> None:
    out = _out()
    out.verdicts[0].evidence[0].chunk = "C9"
    problems = _Validator(EXTRACTION, _ctx())(out)
    assert "trecho C9 não foi enviado" in problems[0]


def test_met_without_evidence_is_rejected() -> None:
    out = _out()
    out.verdicts[0].evidence = []
    assert "exige evidência" in _Validator(EXTRACTION, _ctx())(out)[0]


def test_missing_unknown_and_repeated_ids() -> None:
    out = _out()
    out.verdicts[1].requirement_id = "R7"
    out.verdicts.append(out.verdicts[0].model_copy())
    problems = _Validator(EXTRACTION, _ctx())(out)
    assert any("R7" in p and "inexistente" in p for p in problems)
    assert any("repetido" in p for p in problems)
    assert problems[-1] == "faltam vereditos para: R2"


def test_suggestion_original_must_be_literal() -> None:
    bad = {"chunk": "C1", "original": "texto que não existe", "suggestion": "outro texto"}
    out = _out(suggestions=[bad])
    assert "suggestions.0" in _Validator(EXTRACTION, _ctx())(out)[0]


def test_problems_never_echo_resume_text() -> None:
    out = _out()
    out.verdicts[0].evidence[0].quote = "segredo do candidato"
    assert all("segredo" not in p for p in _Validator(EXTRACTION, _ctx())(out))


def test_build_result_maps_alias_to_chunk_id_and_derives_gaps() -> None:
    ctx = _ctx()
    out = _out()
    out.verdicts[1].evidence = [out.verdicts[0].evidence[0]]  # not_met com evidência: descartada
    result = build_result(EXTRACTION, ctx, out, "fake-llm")

    r1, r2 = result.requirements
    assert r1.evidence[0].chunk_id == ctx.chunks["C1"].id
    assert r2.evidence == []
    assert [g.requirement_id for g in result.gaps] == ["R2"]
    assert result.score == 70  # obrigatório met (70%) e diferencial not_met (0 de 30%)
    assert result.model == "fake-llm"
