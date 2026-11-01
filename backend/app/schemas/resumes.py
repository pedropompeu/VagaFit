import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ResumeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str = Field(examples=["Currículo backend 2026"])
    created_at: datetime
    chunk_count: int = Field(examples=[7])


class ResumeChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ordinal: int
    content: str


class ResumeDetail(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    raw_text: str
    chunks: list[ResumeChunkRead]


class ChunkPreview(BaseModel):
    ordinal: int
    content: str
    estimated_tokens: int


class ResumePreview(BaseModel):
    """Como o texto será dividido, sem salvar nada e sem gerar embedding."""

    chunk_count: int
    chunks: list[ChunkPreview]
