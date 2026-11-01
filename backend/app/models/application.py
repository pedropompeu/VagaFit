import uuid
from datetime import date, datetime

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.job import Job
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin, utcnow

# Código em inglês no banco e na API; o rótulo em português fica no front.
APPLICATION_STATUSES = (
    "sent",  # Enviada
    "in_review",  # Em análise
    "tech_test",  # Teste técnico
    "interview",  # Entrevista
    "offer",  # Proposta
    "rejected",  # Recusada
    "no_response",  # Sem retorno
)


class Application(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Candidatura a uma vaga do dono. Uma por vaga; a análise é opcional."""

    __tablename__ = "applications"
    __table_args__ = (
        CheckConstraint(
            "status IN ({})".format(", ".join(f"'{s}'" for s in APPLICATION_STATUSES)),
            name="status_valid",
        ),
        CheckConstraint(
            "salary_expectation IS NULL OR salary_expectation >= 0", name="salary_non_negative"
        ),
        UniqueConstraint("job_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    job_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("jobs.id", ondelete="CASCADE"))
    analysis_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("analyses.id", ondelete="SET NULL")
    )
    platform: Mapped[str | None] = mapped_column(String(60))
    status: Mapped[str] = mapped_column(String(16), default="sent")
    salary_expectation: Mapped[int | None] = mapped_column(Integer)
    next_step: Mapped[str | None] = mapped_column(String(300))
    applied_at: Mapped[date] = mapped_column(Date)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    job: Mapped[Job] = relationship(lazy="raise")
