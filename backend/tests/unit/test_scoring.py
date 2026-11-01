import pytest

from app.schemas.analysis import RequirementResult
from app.services.scoring import compute_score


def _r(kind: str, verdict: str, i: int = 1) -> RequirementResult:
    return RequirementResult(
        id=f"R{i}", text="x", kind=kind, verdict=verdict, evidence=[], rationale=""
    )


def test_weights_70_30() -> None:
    score, breakdown = compute_score([_r("required", "met"), _r("nice_to_have", "not_met", 2)])
    assert score == 70
    assert breakdown.required == 1.0
    assert breakdown.nice_to_have == 0.0


def test_partial_counts_half() -> None:
    score, _ = compute_score([_r("required", "partial"), _r("required", "met", 2)])
    assert score == 75


@pytest.mark.parametrize("kind", ["required", "nice_to_have"])
def test_single_group_counts_100(kind: str) -> None:
    score, breakdown = compute_score([_r(kind, "met")])
    assert score == 100
    assert (breakdown.required is None) is (kind == "nice_to_have")


def test_empty_is_zero() -> None:
    score, breakdown = compute_score([])
    assert score == 0
    assert breakdown.required is None
    assert breakdown.nice_to_have is None


def test_rounding() -> None:
    results = [_r("required", v, i) for i, v in enumerate(["met", "met", "not_met"], 1)]
    results.append(_r("nice_to_have", "met", 4))
    assert compute_score(results)[0] == 77  # 0.7 * 2/3 + 0.3 = 0.7667
