"""O golden set precisa passar pela validação de saída com o FakeLLMProvider.

Acerto de veredito não é afirmado aqui: o fake é heurístico, e a medida de acerto fica no
relatório de `python -m evals.run`. O que este teste garante é a regra de honestidade: nenhum
caso pode gerar saída inválida (citação fora do trecho recebido ou schema quebrado).
"""

from contextlib import contextmanager
from typing import Any

from app.ai.fake_llm import FakeLLMProvider
from evals.run import CaseResult, load_cases, publish, run_case


async def test_golden_set_outputs_pass_validation_with_fake_llm() -> None:
    llm = FakeLLMProvider()
    cases = load_cases()
    assert cases, "o golden set não pode estar vazio"

    for case in cases:
        result = await run_case(llm, case)
        assert result.valid, (result.case_id, result.problems)


class _StubClient:
    """Registra as chamadas do cliente LangFuse, sem rede."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def create_dataset(self, **kwargs: Any) -> None:
        self.calls.append(("create_dataset", kwargs))

    def create_dataset_item(self, **kwargs: Any) -> None:
        self.calls.append(("create_dataset_item", kwargs))

    @contextmanager
    def start_as_current_observation(self, **kwargs: Any):  # type: ignore[no-untyped-def]
        self.calls.append(("start_as_current_observation", kwargs))
        yield self

    def score_current_trace(self, **kwargs: Any) -> None:
        self.calls.append(("score_current_trace", kwargs))

    def flush(self) -> None:
        self.calls.append(("flush", {}))


def test_publish_sends_dataset_items_and_scores() -> None:
    cases = [{"id": "c1", "resume": "r", "job": "j", "expected": {"Docker": "met"}}]
    results = [CaseResult(case_id="c1", total=1, hits=1, valid=True)]
    client = _StubClient()

    publish(client, cases, results, provider="fake-llm")

    names = [name for name, _ in client.calls]
    assert names[0] == "create_dataset"
    item = next(kwargs for name, kwargs in client.calls if name == "create_dataset_item")
    assert item["id"] == "c1"
    assert item["expected_output"] == {"Docker": "met"}
    scores = {k["name"]: k["value"] for n, k in client.calls if n == "score_current_trace"}
    assert scores == {"verdict_accuracy": 1.0, "valid_output": 1.0}
    assert names[-1] == "flush"
