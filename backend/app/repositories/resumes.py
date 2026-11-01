"""Acesso a `resumes` e `resume_chunks`. Toda query filtra pelo dono (`user_id`)."""

import uuid
from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.resume import Resume, ResumeChunk


@dataclass(frozen=True)
class ResumeSummary:
    resume: Resume
    chunk_count: int


@dataclass(frozen=True)
class ChunkMatch:
    chunk: ResumeChunk
    distance: float


class ResumeRepository:
    def __init__(self, session: AsyncSession, user_id: uuid.UUID) -> None:
        self._session = session
        self._user_id = user_id

    async def add(
        self, *, title: str, raw_text: str, chunks: list[tuple[str, list[float]]]
    ) -> Resume:
        resume = Resume(user_id=self._user_id, title=title, raw_text=raw_text)
        resume.chunks = [
            ResumeChunk(ordinal=i, content=content, embedding=vector)
            for i, (content, vector) in enumerate(chunks)
        ]
        self._session.add(resume)
        await self._session.flush()
        return resume

    async def list_all(self) -> list[ResumeSummary]:
        counts = (
            select(ResumeChunk.resume_id, func.count().label("n"))
            .group_by(ResumeChunk.resume_id)
            .subquery()
        )
        rows = await self._session.execute(
            select(Resume, func.coalesce(counts.c.n, 0))
            .outerjoin(counts, counts.c.resume_id == Resume.id)
            .where(Resume.user_id == self._user_id)
            .order_by(Resume.created_at.desc(), Resume.id)
        )
        return [ResumeSummary(resume=r, chunk_count=int(n)) for r, n in rows]

    async def get(self, resume_id: uuid.UUID, *, with_chunks: bool = False) -> Resume | None:
        query = select(Resume).where(Resume.id == resume_id, Resume.user_id == self._user_id)
        if with_chunks:
            query = query.options(selectinload(Resume.chunks))
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def delete(self, resume_id: uuid.UUID) -> bool:
        result = await self._session.execute(
            delete(Resume)
            .where(Resume.id == resume_id, Resume.user_id == self._user_id)
            .returning(Resume.id)
        )
        return result.scalar_one_or_none() is not None

    async def get_chunks(self, resume_id: uuid.UUID) -> list[ResumeChunk]:
        result = await self._session.execute(
            select(ResumeChunk)
            .join(Resume, Resume.id == ResumeChunk.resume_id)
            .where(ResumeChunk.resume_id == resume_id, Resume.user_id == self._user_id)
            .order_by(ResumeChunk.ordinal)
        )
        return list(result.scalars())

    async def nearest_chunks(
        self, resume_id: uuid.UUID, vector: list[float], *, k: int
    ) -> list[ChunkMatch]:
        """Os k chunks mais próximos (distância de cosseno) dentro de um currículo do usuário."""
        distance = ResumeChunk.embedding.cosine_distance(vector).label("distance")
        result = await self._session.execute(
            select(ResumeChunk, distance)
            .join(Resume, Resume.id == ResumeChunk.resume_id)
            .where(ResumeChunk.resume_id == resume_id, Resume.user_id == self._user_id)
            .order_by(distance, ResumeChunk.ordinal)
            .limit(k)
        )
        return [ChunkMatch(chunk=c, distance=float(d)) for c, d in result]
