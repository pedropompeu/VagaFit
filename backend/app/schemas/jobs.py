import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.extraction import JobExtraction

ExtractionStatus = Literal["pending", "done"]

JOB_TEXT_MAX_CHARS = 30_000


class JobCreate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=160,
        description="Cargo. Se omitido, usa a primeira linha do texto.",
        examples=["Pessoa Desenvolvedora Backend Python"],
    )
    company: str | None = Field(default=None, min_length=1, max_length=160, examples=["Acme"])
    raw_text: str = Field(
        min_length=20,
        max_length=JOB_TEXT_MAX_CHARS,
        description="Texto da vaga colado.",
    )


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    company: str | None
    created_at: datetime
    extraction_status: ExtractionStatus = Field(
        description="`pending` até o worker extrair os requisitos; `done` depois."
    )


class JobDetail(JobRead):
    raw_text: str
    extracted: JobExtraction | None
