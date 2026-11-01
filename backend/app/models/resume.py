import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.ai.embeddings import EMBEDDING_DIMENSIONS
from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class Resume(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Currículo do usuário. `raw_text` é o texto normalizado (nunca vai para o log)."""

    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(120))
    raw_text: Mapped[str] = mapped_column(Text)

    chunks: Mapped[list["ResumeChunk"]] = relationship(
        back_populates="resume",
        order_by="ResumeChunk.ordinal",
        cascade="all, delete-orphan",
        passive_deletes=True,
        lazy="raise",
    )


class ResumeChunk(UUIDPrimaryKeyMixin, Base):
    """Trecho do currículo com embedding. É a unidade citada como evidência (`chunk_id`).

    Sem índice ANN (HNSW): a busca é sempre dentro de um currículo (dezenas de chunks), e
    o filtro por `resume_id` num índice aproximado pode devolver menos de k resultados.
    """

    __tablename__ = "resume_chunks"
    __table_args__ = (UniqueConstraint("resume_id", "ordinal"),)

    resume_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("resumes.id", ondelete="CASCADE"), index=True
    )
    ordinal: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSIONS))

    resume: Mapped[Resume] = relationship(back_populates="chunks", lazy="raise")
