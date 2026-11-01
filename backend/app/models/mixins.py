"""Colunas comuns. Todo model usa UUID como chave primária (ID sequencial facilita enumeração)."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(UTC)


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)


class CreatedAtMixin:
    # Default em Python (valor disponível logo após o insert, sem refresh) e no banco.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, server_default=func.now()
    )
