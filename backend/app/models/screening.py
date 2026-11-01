import uuid
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UUIDPrimaryKeyMixin


class ScreeningAnswer(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    """Rascunho de resposta a uma pergunta de triagem, ligado a uma análise `done`.

    O dono é o dono da análise (sem `user_id` próprio): toda leitura passa pela análise.
    `evidence` guarda `[{chunk_id, quote}]`; `evidence_chunk_ids` sai dela.
    """

    __tablename__ = "screening_answers"

    analysis_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("analyses.id", ondelete="CASCADE"), index=True
    )
    ordinal: Mapped[int] = mapped_column(Integer)
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text, default="")
    evidence: Mapped[list[dict[str, Any]]] = mapped_column(JSONB, default=list)
    needs_user_input: Mapped[bool] = mapped_column(Boolean, default=False)
    user_question: Mapped[str | None] = mapped_column(Text)
