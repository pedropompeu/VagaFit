import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin

ANALYSIS_STATUSES = ("pending", "running", "done", "failed")


class Analysis(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Análise de um currículo contra uma vaga. Roda no worker; `result` só quando `done`."""

    __tablename__ = "analyses"
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'running', 'done', 'failed')", name="status_valid"),
        CheckConstraint("score IS NULL OR (score BETWEEN 0 AND 100)", name="score_range"),
        Index("ix_analyses_user_id_input_hash", "user_id", "input_hash"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    resume_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("resumes.id", ondelete="CASCADE"), index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("jobs.id", ondelete="CASCADE"), index=True
    )
    status: Mapped[str] = mapped_column(String(16), default="pending")
    score: Mapped[int | None] = mapped_column(Integer)
    result: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    input_hash: Mapped[str] = mapped_column(String(64))
    error: Mapped[str | None] = mapped_column(Text)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
