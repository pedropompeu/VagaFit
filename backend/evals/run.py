"""Avaliação offline da análise contra o golden set (ADR-002: próximo passo de qualidade).

Uso (no container da API): `python -m evals.run`. O provedor vem de `LLM_PROVIDER`; o padrão é
o `fake`, que serve de teste de regressão, não de medida de qualidade.

Sem banco e sem embeddings: o currículo é quebrado com o chunker do app e todos os trechos
são candidatos a cada requisito. A recuperação real (top-k por embedding) é mais restrita, então
aqui o veredito tem uma chance maior de acertar. A regra de honestidade é verificada do mesmo
jeito: citação fora do trecho recebido reprova o caso.

Métricas: acerto de veredito (por requisito) e saídas inválidas (validação falhou nas duas
tentativas). Saídas inválidas dão código de saída 1.
"""

import asyncio
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.ai.llm import LLMOutputError, LLMProvider, build_llm_provider, structured_call
from app.core.config import get_settings
from app.models.resume import ResumeChunk
from app.schemas.analysis import LLMAnalysis
from app.services.analysis import _analysis_request, _Validator
from app.services.chunking import chunk_resume
from app.services.job_extraction import extract_requirements
from app.services.retrieval import RetrievedContext
from app.services.text import normalize_for_match

GOLDEN_SET = Path(__file__).with_name("golden_set.json")


@dataclass
class CaseResult:
    case_id: str
    total: int
    hits: int = 0
    valid: bool = True
    problems: list[str] = field(default_factory=list)
    mismatches: list[str] = field(default_factory=list)


def load_cases(path: Path = GOLDEN_SET) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = json.loads(path.read_text(encoding="utf-8"))
    return cases


async def run_case(llm: LLMProvider, case: dict[str, Any]) -> CaseResult:
    expected: dict[str, str] = case["expected"]
    result = CaseResult(case_id=case["id"], total=len(expected))
    try:
        extraction = await extract_requirements(llm, case["job"])
        chunks = {
            f"C{i}": ResumeChunk(content=text)
            for i, text in enumerate(chunk_resume(case["resume"]), start=1)
        }
        aliases = list(chunks)
        ctx = RetrievedContext(
            chunks=chunks, candidates={r.id: aliases for r in extraction.requirements}
        )
        output = await structured_call(
            llm,
            _analysis_request(extraction, ctx),
            LLMAnalysis,
            _Validator(extraction, ctx),
        )
    except LLMOutputError as exc:
        result.valid = False
        result.problems = [f"{exc.task}: {p}" for p in exc.problems]
        return result

    ids_by_text = {normalize_for_match(r.text): r.id for r in extraction.requirements}
    verdicts = {v.requirement_id: v.verdict for v in output.verdicts}
    for text, want in expected.items():
        req_id = ids_by_text.get(normalize_for_match(text))
        got = verdicts.get(req_id) if req_id else None
        if got == want:
            result.hits += 1
        else:
            result.mismatches.append(f"{text!r}: esperado {want}, veio {got or 'não extraído'}")
    return result


def _print_report(results: list[CaseResult], provider: str) -> None:
    for r in results:
        status = "ok" if r.valid else "INVÁLIDO"
        print(f"[{status}] {r.case_id}: {r.hits}/{r.total} vereditos certos")
        for mismatch in r.mismatches:
            print(f"    - {mismatch}")
        for problem in r.problems:
            print(f"    ! {problem}")
    hits = sum(r.hits for r in results)
    total = sum(r.total for r in results)
    invalid = sum(not r.valid for r in results)
    print(
        f"\nProvedor: {provider} · casos: {len(results)} · "
        f"acerto de veredito: {hits}/{total} · saídas inválidas: {invalid}"
    )


async def main() -> int:
    llm = build_llm_provider(get_settings())
    try:
        results = [await run_case(llm, case) for case in load_cases()]
    finally:
        await llm.aclose()
    _print_report(results, llm.model)
    return 1 if any(not r.valid for r in results) else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
