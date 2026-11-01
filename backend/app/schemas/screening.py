"""Perguntas de triagem: entrada, o que o LLM devolve e o que a API responde."""

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, computed_field

from app.schemas.analysis import Evidence, LLMEvidence

MAX_QUESTIONS = 10


Question = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=500)]


class ScreeningRequest(BaseModel):
    questions: list[Question] = Field(
        min_length=1,
        max_length=MAX_QUESTIONS,
        description=f"Perguntas de triagem da vaga, até {MAX_QUESTIONS}.",
        examples=[["Você tem experiência com FastAPI?", "Qual sua pretensão salarial?"]],
    )


class LLMScreeningAnswer(BaseModel):
    question_id: str = Field(description="ID da pergunta recebida, ex.: Q1.")
    answer: str = Field(
        max_length=1500,
        description="Rascunho em primeira pessoa, só com fatos dos trechos citados.",
    )
    evidence: list[LLMEvidence] = Field(max_length=3)
    needs_user_input: bool = Field(
        description="true quando os trechos não bastam para responder sem inventar."
    )
    user_question: str | None = Field(
        max_length=300,
        description="Pergunta objetiva ao candidato quando needs_user_input = true; senão null.",
    )


class LLMScreening(BaseModel):
    answers: list[LLMScreeningAnswer]


class ScreeningAnswerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    analysis_id: uuid.UUID
    question: str
    answer: str
    evidence: list[Evidence]
    needs_user_input: bool
    user_question: str | None
    created_at: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def evidence_chunk_ids(self) -> list[uuid.UUID]:
        return list(dict.fromkeys(e.chunk_id for e in self.evidence))
