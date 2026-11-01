"""Acesso a `jobs`. Toda query filtra pelo dono (`user_id`)."""

import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


class JobRepository:
    def __init__(self, session: AsyncSession, user_id: uuid.UUID) -> None:
        self._session = session
        self._user_id = user_id

    async def add(self, *, title: str, company: str | None, raw_text: str) -> Job:
        job = Job(user_id=self._user_id, title=title, company=company, raw_text=raw_text)
        self._session.add(job)
        await self._session.flush()
        return job

    async def list_all(self) -> list[Job]:
        result = await self._session.execute(
            select(Job).where(Job.user_id == self._user_id).order_by(Job.created_at.desc(), Job.id)
        )
        return list(result.scalars())

    async def get(self, job_id: uuid.UUID) -> Job | None:
        result = await self._session.execute(
            select(Job).where(Job.id == job_id, Job.user_id == self._user_id)
        )
        return result.scalar_one_or_none()

    async def set_extracted(self, job: Job, extracted: dict[str, Any]) -> None:
        job.extracted = extracted
        await self._session.flush()

    async def delete(self, job_id: uuid.UUID) -> bool:
        result = await self._session.execute(
            delete(Job).where(Job.id == job_id, Job.user_id == self._user_id).returning(Job.id)
        )
        return result.scalar_one_or_none() is not None
