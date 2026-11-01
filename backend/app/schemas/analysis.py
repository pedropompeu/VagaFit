"""Formatos da análise: o que o LLM devolve, o que fica em `analyses.result` e o que a API expõe.

O LLM cita trechos por alias curto (`C1`, `C2`...) que o código traduz para o `chunk_id`
real. Isso reduz tokens e impede que o modelo "invente" um UUID plausível.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.extraction import RequirementKind, Seniority, WorkModel

Verdict = Literal["met", "partial", "not_met"]
AnalysisStatus = Literal["pending", "running", "done", "failed"]


# --- saída do LLM ---------------------------------------------------------------------


class LLMEvidence(BaseModel):
    chunk: str = Field(description="Alias do trecho citado, ex.: C2. Só os recebidos.")
    quote: str = Field(
        min_length=3,
        max_length=400,
        description="Cópia literal de parte do trecho que sustenta o veredito.",
    )


class LLMVerdict(BaseModel):
    requirement_id: str = Field(description="ID do requisito, ex.: R1.")
    verdict: Verdict = Field(
        description=(
            "met = atende; partial = atende em parte; not_met = não atende ou sem evidência."
        )
    )
    evidence: list[LLMEvidence] = Field(
        max_length=3, description="Obrigatória em met e partial. Vazia em not_met."
    )
    rationale: str = Field(
        max_length=300,
        description="Uma frase que só relaciona a evidência ao requisito, sem fato novo.",
    )


class LLMSuggestion(BaseModel):
    chunk: str = Field(description="Alias do trecho que a sugestão reescreve.")
    original: str = Field(min_length=3, max_length=400, description="Trecho literal atual.")
    suggestion: str = Field(
        min_length=3,
        max_length=600,
        description="Reescrita que só reorganiza ou destaca o que já está no original.",
    )


class LLMAnalysis(BaseModel):
    verdicts: list[LLMVerdict]
    suggestions: list[LLMSuggestion] = Field(max_length=5)


# --- resultado salvo ------------------------------------------------------------------


class Evidence(BaseModel):
    chunk_id: uuid.UUID
    quote: str


class RequirementResult(BaseModel):
    id: str
    text: str
    kind: RequirementKind
    verdict: Verdict
    evidence: list[Evidence]
    rationale: str


class Gap(BaseModel):
    requirement_id: str
    text: str
    kind: RequirementKind
    verdict: Literal["partial", "not_met"]


class Suggestion(BaseModel):
    chunk_id: uuid.UUID
    original: str
    suggestion: str


class ScoreBreakdown(BaseModel):
    """Aderência de 0 a 1 por grupo; `None` quando a vaga não tem requisitos do grupo."""

    required: float | None
    nice_to_have: float | None


class JobSummary(BaseModel):
    title: str | None
    seniority: Seniority
    work_model: WorkModel
    stack: list[str]


class AnalysisResult(BaseModel):
    score: int = Field(ge=0, le=100)
    breakdown: ScoreBreakdown
    job: JobSummary
    requirements: list[RequirementResult]
    gaps: list[Gap]
    suggestions: list[Suggestion]
    model: str
    prompt_version: str


# --- API ------------------------------------------------------------------------------


class AnalysisCreate(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID


class AnalysisRead(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID
    status: AnalysisStatus
    score: int | None
    error: str | None
    created_at: datetime
    finished_at: datetime | None


class AnalysisCreated(AnalysisRead):
    reused: bool = Field(
        description="true quando devolveu uma análise igual já existente (cache por hash)."
    )


class AnalysisDetail(AnalysisRead):
    result: AnalysisResult | None
