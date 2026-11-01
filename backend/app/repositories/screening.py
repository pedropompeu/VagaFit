"""Acesso a `screening_answers`. O isolamento vem da análise: o service só chega aqui
depois de carregar a análise pelo dono (`AnalysisRepository`); a leitura junta com
`analyses` e filtra por `user_id` mesmo assim.
"""

import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis
from app.models.screening import ScreeningAnswer


class ScreeningRepository:
    def __init__(self, session: AsyncSession, user_id: uuid.UUID) -> None:
        self._session = session
        self._user_id = user_id

    async def add_many(
        self, analysis_id: uuid.UUID, rows: list[dict[str, Any]]
    ) -> list[ScreeningAnswer]:
        answers = [ScreeningAnswer(analysis_id=analysis_id, **row) for row in rows]
        self._session.add_all(answers)
        await self._session.flush()
        return answers

    async def list_for(self, analysis_id: uuid.UUID) -> list[ScreeningAnswer]:
        result = await self._session.execute(
            select(ScreeningAnswer)
            .join(Analysis, Analysis.id == ScreeningAnswer.analysis_id)
            .where(ScreeningAnswer.analysis_id == analysis_id, Analysis.user_id == self._user_id)
            .order_by(ScreeningAnswer.created_at, ScreeningAnswer.ordinal)
        )
        return list(result.scalars())
