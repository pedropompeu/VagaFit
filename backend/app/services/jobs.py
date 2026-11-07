"""CRUD de vagas do dono. Criar uma vaga enfileira a extração de requisitos no worker."""

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.models.job import Job
from app.repositories.jobs import JobRepository
from app.schemas.jobs import JobCreate
from app.services.text import normalize_document
from app.worker.queue import EXTRACT_JOB_TASK, TaskQueue

logger = structlog.get_logger(__name__)

JOB_NOT_FOUND = "Vaga não encontrada."


def _first_line(text: str) -> str:
    return next((line.strip() for line in text.split("\n") if line.strip()), "Vaga")[:160]


class JobService:
    def __init__(self, session: AsyncSession, user_id: uuid.UUID, queue: TaskQueue) -> None:
        self._session = session
        self._user_id = user_id
        self._queue = queue
        self._repo = JobRepository(session, user_id)

    async def create(self, data: JobCreate) -> Job:
        text = normalize_document(data.raw_text)
        job = await self._repo.add(
            title=(data.title or _first_line(text)).strip(),
            company=data.company.strip() if data.company else None,
            raw_text=text,
        )
        await self._session.commit()
        # Depois do commit: o worker precisa enxergar a linha.
        self._queue.enqueue(EXTRACT_JOB_TASK, str(job.id), str(self._user_id))
        logger.info("job.created", job_id=str(job.id))
        return job

    async def list_all(self) -> list[Job]:
        return await self._repo.list_all()

    async def get(self, job_id: uuid.UUID) -> Job:
        job = await self._repo.get(job_id)
        if job is None:
            raise NotFoundError(JOB_NOT_FOUND)
        return job

    async def retry_extraction(self, job_id: uuid.UUID) -> Job:
        """Reenfileira a extração de uma vaga que falhou. Vaga já extraída não muda."""
        job = await self.get(job_id)
        if job.extracted is None:
            await self._repo.clear_extraction_error(job)
            await self._session.commit()
            self._queue.enqueue(EXTRACT_JOB_TASK, str(job.id), str(self._user_id))
            logger.info("job.extraction_retried", job_id=str(job.id))
        return job

    async def delete(self, job_id: uuid.UUID) -> None:
        if not await self._repo.delete(job_id):
            raise NotFoundError(JOB_NOT_FOUND)
        await self._session.commit()
        logger.info("job.deleted", job_id=str(job_id))
