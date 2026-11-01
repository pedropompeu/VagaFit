"""Extração de requisitos da vaga: o que o LLM devolve e o que fica em `jobs.extracted`."""

from typing import Literal

from pydantic import BaseModel, Field

Seniority = Literal["intern", "junior", "mid", "senior", "lead", "unspecified"]
WorkModel = Literal["remote", "hybrid", "onsite", "unspecified"]
RequirementKind = Literal["required", "nice_to_have"]

MAX_REQUIREMENTS = 40


class LLMRequirement(BaseModel):
    text: str = Field(min_length=2, max_length=300, description="Requisito como está na vaga.")
    kind: RequirementKind = Field(
        description="required = obrigatório; nice_to_have = diferencial/desejável."
    )


class LLMJobExtraction(BaseModel):
    """Saída do LLM. Os IDs dos requisitos são atribuídos no código, não pelo modelo."""

    title: str | None = Field(description="Cargo, se a vaga disser. Senão null.")
    company: str | None = Field(description="Empresa, se a vaga disser. Senão null.")
    seniority: Seniority
    work_model: WorkModel
    location: str | None
    stack: list[str] = Field(description="Tecnologias citadas na vaga, sem inventar.")
    requirements: list[LLMRequirement] = Field(min_length=1, max_length=MAX_REQUIREMENTS)


class Requirement(LLMRequirement):
    id: str = Field(examples=["R1"])


class JobExtraction(BaseModel):
    """Como fica salvo em `jobs.extracted` (com modelo e versão do prompt para auditoria)."""

    title: str | None
    company: str | None
    seniority: Seniority
    work_model: WorkModel
    location: str | None
    stack: list[str]
    requirements: list[Requirement]
    model: str
    prompt_version: str
