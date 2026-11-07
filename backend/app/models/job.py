import uuid
from typing import Any

from sqlalchemy import ForeignKey, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class Job(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Vaga colada pelo usuário. `extracted` fica nulo até a extração de requisitos rodar."""

    __tablename__ = "jobs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(160))
    company: Mapped[str | None] = mapped_column(String(160))
    raw_text: Mapped[str] = mapped_column(Text)
    extracted: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    # Motivo curto da última falha de extração; nulo quando não falhou (ou quando deu certo).
    extraction_error: Mapped[str | None] = mapped_column(String(200))
