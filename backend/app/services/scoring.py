"""Score de aderência calculado no código, nunca pelo LLM.

Obrigatórios pesam 70% e diferenciais 30%; `partial` vale metade. Se a vaga não tiver um
dos grupos, o outro vale 100% (sem isso, uma vaga sem diferenciais teria teto de 70).
"""

from collections.abc import Sequence

from app.schemas.analysis import RequirementResult, ScoreBreakdown, Verdict

REQUIRED_WEIGHT = 0.7
NICE_TO_HAVE_WEIGHT = 0.3
VERDICT_VALUE: dict[Verdict, float] = {"met": 1.0, "partial": 0.5, "not_met": 0.0}


def _group(results: Sequence[RequirementResult], kind: str) -> float | None:
    values = [VERDICT_VALUE[r.verdict] for r in results if r.kind == kind]
    return sum(values) / len(values) if values else None


def compute_score(results: Sequence[RequirementResult]) -> tuple[int, ScoreBreakdown]:
    required = _group(results, "required")
    nice = _group(results, "nice_to_have")
    breakdown = ScoreBreakdown(required=required, nice_to_have=nice)
    # Grupo ausente sai da conta e o peso é redistribuído (70/30 vira 100/0).
    parts = [
        (weight, value)
        for weight, value in ((REQUIRED_WEIGHT, required), (NICE_TO_HAVE_WEIGHT, nice))
        if value is not None
    ]
    if not parts:
        return 0, breakdown
    total = sum(w * v for w, v in parts) / sum(w for w, _ in parts)
    return round(total * 100), breakdown
