import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class RefreshToken(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Um refresh token emitido. Guarda só o SHA-256 do valor entregue no cookie.

    Cada login abre uma família (`family_id`). Cada uso gira o token: o atual é revogado e
    aponta para o novo em `replaced_by_id`. Se um token já girado voltar, é sinal de roubo e
    a família inteira é revogada.
    """

    __tablename__ = "refresh_tokens"

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    family_id: Mapped[uuid.UUID] = mapped_column(Uuid, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    replaced_by_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("refresh_tokens.id", ondelete="SET NULL")
    )
