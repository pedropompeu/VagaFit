"""O FakeLLMProvider precisa produzir saídas que passam no schema e na validação de evidência.

Regressão: currículo colado em um parágrafo só virava uma linha de 454 caracteres. O fake
citava a linha inteira, o schema recusava `quote` acima de 400, e a análise falhava.
"""

from types import SimpleNamespace

from app.ai.fake_llm import _QUOTE_MAX, analyze_fit
from app.schemas.analysis import LLMAnalysis
from app.services.analysis import _Validator
from app.services.text import quote_in_text

RESUME_ONE_PARAGRAPH = (
    "Ana Souza, Engenheira de Software Backend. Experiência: 2021-2026: Desenvolvedora "
    "Python na Acme. Construí APIs REST com FastAPI e PostgreSQL, atendendo 40 mil usuários "
    "por mês. Escrevi testes com pytest e cobertura acima de 85%. 2019-2021: Desenvolvedora "
    "Full Stack na Beta Tech. Front-end em React e back-end em Django. Habilidades: Python, "
    "FastAPI, SQLAlchemy, PostgreSQL, Docker, React, TypeScript, pytest. Idiomas: português "
    "nativo, inglês avançado."
)
REQUIREMENTS = [
    "experiência com Python e FastAPI",
    "banco relacional (PostgreSQL)",
    "testes automatizados",
    "Docker",
]


def _request_and_context(resume: str, requirements: list[str]):
    chunks = {"C1": resume}
    payload = {
        "chunks": chunks,
        "requirements": [
            {"id": f"R{i + 1}", "text": text, "kind": "required", "candidates": ["C1"]}
            for i, text in enumerate(requirements)
        ],
    }
    request = SimpleNamespace(payload=payload)
    ctx = SimpleNamespace(chunks={"C1": SimpleNamespace(content=resume)}, candidates={})
    extraction = SimpleNamespace(
        requirements=[SimpleNamespace(id=f"R{i + 1}") for i in range(len(requirements))]
    )
    return request, ctx, extraction


def test_long_single_line_resume_gets_bounded_literal_quotes() -> None:
    assert len(RESUME_ONE_PARAGRAPH) > _QUOTE_MAX  # o caso reproduz o problema

    request, _, _ = _request_and_context(RESUME_ONE_PARAGRAPH, REQUIREMENTS)
    output = analyze_fit(request)

    quotes = [ev["quote"] for v in output["verdicts"] for ev in v["evidence"]]
    quotes += [s["original"] for s in output["suggestions"]]
    assert quotes
    for quote in quotes:
        assert len(quote) <= _QUOTE_MAX
        assert quote_in_text(quote, RESUME_ONE_PARAGRAPH)


def test_long_single_line_resume_passes_schema_and_evidence_validation() -> None:
    request, ctx, extraction = _request_and_context(RESUME_ONE_PARAGRAPH, REQUIREMENTS)
    output = LLMAnalysis.model_validate(analyze_fit(request))

    assert _Validator(extraction, ctx)(output) == []


def test_met_verdict_is_supported_by_its_own_quote() -> None:
    request, _, _ = _request_and_context(RESUME_ONE_PARAGRAPH, REQUIREMENTS)
    output = analyze_fit(request)

    verdicts = {v["requirement_id"]: v for v in output["verdicts"]}
    # "Docker" só aparece na lista de habilidades; a citação precisa conter a palavra.
    docker_quote = verdicts["R4"]["evidence"][0]["quote"]
    assert "Docker" in docker_quote


JOB_ONE_PARAGRAPH = (
    "Pessoa Desenvolvedora Backend Python Requisitos: experiência com Python e FastAPI; "
    "banco relacional (PostgreSQL); testes automatizados; Docker. Diferencial: React e "
    "TypeScript. Sobre a vaga: time de produto em remoto, foco em APIs de alta disponibilidade."
)


def test_one_paragraph_job_yields_requirements_that_pass_the_schema() -> None:
    """Regressão: vaga sem quebra de linha ficava sem requisitos e a extração era rejeitada."""
    from app.ai.fake_llm import extract_requirements
    from app.schemas.extraction import LLMJobExtraction

    out = extract_requirements(SimpleNamespace(payload={"job_text": JOB_ONE_PARAGRAPH}))
    parsed = LLMJobExtraction.model_validate(out)

    texts = [r.text for r in parsed.requirements]
    assert "banco relacional (PostgreSQL)" in texts
    assert all(len(t) <= 300 for t in texts)
    assert not any(t.startswith("Pessoa Desenvolvedora") for t in texts)  # título fora
    assert not any("Sobre a vaga" in t for t in texts)  # descrição fora
    diff = [r for r in parsed.requirements if r.text == "React e TypeScript"]
    assert [r.kind for r in diff] == ["nice_to_have"]
