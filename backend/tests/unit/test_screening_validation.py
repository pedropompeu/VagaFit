import uuid

from app.models.resume import ResumeChunk
from app.schemas.screening import LLMScreening
from app.services.analysis import RetrievedContext
from app.services.screening import _Validator

CHUNK = "- Criei APIs REST em FastAPI."
CTX = RetrievedContext(
    chunks={"C1": ResumeChunk(id=uuid.uuid4(), content=CHUNK, ordinal=0)},
    candidates={"Q1": ["C1"], "Q2": ["C1"]},
)


def _answer(qid: str, **overrides: object) -> dict:
    data: dict = {
        "question_id": qid,
        "answer": "Sim, criei APIs em FastAPI.",
        "evidence": [{"chunk": "C1", "quote": "Criei APIs REST em FastAPI."}],
        "needs_user_input": False,
        "user_question": None,
    }
    data.update(overrides)
    return data


def _check(*answers: dict) -> list[str]:
    return _Validator(["Q1", "Q2"], CTX)(LLMScreening.model_validate({"answers": list(answers)}))


def test_valid() -> None:
    asks = _answer("Q2", needs_user_input=True, user_question="Quanto?")
    assert _check(_answer("Q1"), asks) == []


def test_answer_without_evidence_must_ask_user() -> None:
    problems = _check(_answer("Q1", evidence=[]), _answer("Q2"))
    assert problems == ["answers.0 (Q1): resposta sem evidência; use needs_user_input"]


def test_needs_user_input_requires_question() -> None:
    problems = _check(_answer("Q1"), _answer("Q2", needs_user_input=True, user_question=" "))
    assert problems == ["answers.1 (Q2): needs_user_input exige `user_question`"]


def test_empty_answer_rejected() -> None:
    problems = _check(_answer("Q1", answer="  "), _answer("Q2"))
    assert problems == ["answers.0 (Q1): resposta vazia; use needs_user_input"]


def test_quote_checked_even_when_asking_user() -> None:
    bad = [{"chunk": "C1", "quote": "inventado"}]
    problems = _check(
        _answer("Q1"), _answer("Q2", needs_user_input=True, user_question="Quanto?", evidence=bad)
    )
    assert problems == ["answers.1 (Q2).evidence.0: a citação não é cópia literal do trecho C1"]


def test_unknown_repeated_and_missing_ids() -> None:
    problems = _check(_answer("Q1"), _answer("Q1"), _answer("Q9"))
    assert "answers.1 (Q1): pergunta repetida" in problems
    assert "answers.2 (Q9): pergunta inexistente" in problems
    assert problems[-1] == "faltam respostas para: Q2"
