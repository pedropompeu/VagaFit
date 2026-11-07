"""O golden set precisa passar pela validação de saída com o FakeLLMProvider.

Acerto de veredito não é afirmado aqui: o fake é heurístico, e a medida de acerto fica no
relatório de `python -m evals.run`. O que este teste garante é a regra de honestidade: nenhum
caso pode gerar saída inválida (citação fora do trecho recebido ou schema quebrado).
"""

from app.ai.fake_llm import FakeLLMProvider
from evals.run import load_cases, run_case


async def test_golden_set_outputs_pass_validation_with_fake_llm() -> None:
    llm = FakeLLMProvider()
    cases = load_cases()
    assert cases, "o golden set não pode estar vazio"

    for case in cases:
        result = await run_case(llm, case)
        assert result.valid, (result.case_id, result.problems)
