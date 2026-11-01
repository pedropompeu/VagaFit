"""Acesso a `analyses`. Toda query filtra pelo dono (`user_id`)."""

import uuid
from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import Analysis


class AnalysisRepository:
    def __init__(self, session: AsyncSession, user_id: uuid.UUID) -> None:
        self._session = session
        self._user_id = user_id

    async def add(self, *, resume_id: uuid.UUID, job_id: uuid.UUID, input_hash: str) -> Analysis:
        analysis = Analysis(
            user_id=self._user_id,
            resume_id=resume_id,
            job_id=job_id,
            input_hash=input_hash,
            status="pending",
        )
        self._session.add(analysis)
        await self._session.flush()
        return analysis

    async def get(self, analysis_id: uuid.UUID) -> Analysis | None:
        result = await self._session.execute(
            select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == self._user_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self, *, job_id: uuid.UUID | None = None) -> list[Analysis]:
        query = select(Analysis).where(Analysis.user_id == self._user_id)
        if job_id is not None:
            query = query.where(Analysis.job_id == job_id)
        result = await self._session.execute(
            query.order_by(Analysis.created_at.desc(), Analysis.id)
        )
        return list(result.scalars())

    async def find_reusable(
        self,
        *,
        resume_id: uuid.UUID,
        job_id: uuid.UUID,
        input_hash: str,
        active_since: datetime,
    ) -> Analysis | None:
        """Análise do mesmo par (currículo, vaga) e mesmo hash, pronta ou em andamento recente.

        `failed` nunca é reaproveitada. O par entra no filtro porque a evidência aponta
        para chunks deste currículo e a candidatura aponta para esta vaga.
        """
        result = await self._session.execute(
            select(Analysis)
            .where(
                Analysis.user_id == self._user_id,
                Analysis.resume_id == resume_id,
                Analysis.job_id == job_id,
                Analysis.input_hash == input_hash,
                or_(
                    Analysis.status == "done",
                    Analysis.status.in_(("pending", "running"))
                    & (Analysis.created_at >= active_since),
                ),
            )
            .order_by(Analysis.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
