"""Candidaturas: entrada, atualização parcial e saída."""

import uuid
from datetime import date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

ApplicationStatus = Literal[
    "sent", "in_review", "tech_test", "interview", "offer", "rejected", "no_response"
]

_Platform = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=60)]
_NextStep = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=300)]


class _Editable(BaseModel):
    platform: _Platform | None = Field(default=None, examples=["LinkedIn"])
    salary_expectation: int | None = Field(
        default=None, ge=0, le=10_000_000, description="Pretensão mensal em reais.", examples=[9000]
    )
    next_step: _NextStep | None = Field(default=None, examples=["Entrevista técnica dia 12"])


class ApplicationCreate(_Editable):
    job_id: uuid.UUID
    analysis_id: uuid.UUID | None = Field(
        default=None, description="Análise desta vaga usada para decidir (opcional)."
    )
    status: ApplicationStatus = "sent"
    applied_at: date | None = Field(default=None, description="Padrão: hoje.")


class ApplicationUpdate(_Editable):
    """Só os campos enviados mudam. `null` apaga o campo opcional."""

    analysis_id: uuid.UUID | None = None
    status: ApplicationStatus | None = None
    applied_at: date | None = None

    @model_validator(mode="after")
    def _required_not_null(self) -> "ApplicationUpdate":
        for name in ("status", "applied_at"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"`{name}` não pode ser null")
        return self


class JobRef(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company: str | None


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job: JobRef
    analysis_id: uuid.UUID | None
    platform: str | None
    status: ApplicationStatus
    salary_expectation: int | None
    next_step: str | None
    applied_at: date
    created_at: datetime
    updated_at: datetime
