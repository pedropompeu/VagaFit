"""Candidaturas do dono: uma por vaga, ligada opcionalmente a uma análise da mesma vaga."""

import uuid
from collections.abc import Sequence
from datetime import date
from http import HTTPStatus

import structlog
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError, ConflictError, NotFoundError
from app.models.application import Application
from app.repositories.analyses import AnalysisRepository
from app.repositories.applications import ApplicationRepository
from app.repositories.jobs import JobRepository
from app.schemas.applications import ApplicationCreate, ApplicationUpdate
from app.services.analysis import ANALYSIS_NOT_FOUND
from app.services.jobs import JOB_NOT_FOUND

logger = structlog.get_logger(__name__)

APPLICATION_NOT_FOUND = "Candidatura não encontrada."
ALREADY_APPLIED = "Já existe uma candidatura para esta vaga."
ANALYSIS_OTHER_JOB = "A análise informada é de outra vaga."


class ApplicationService:
    def __init__(self, session: AsyncSession, user_id: uuid.UUID) -> None:
        self._session = session
        self._user_id = user_id
        self._repo = ApplicationRepository(session, user_id)

    async def create(self, data: ApplicationCreate) -> Application:
        job = await JobRepository(self._session, self._user_id).get(data.job_id)
        if job is None:
            raise NotFoundError(JOB_NOT_FOUND)
        if await self._repo.get_by_job(job.id) is not None:
            raise ConflictError(ALREADY_APPLIED)
        await self._check_analysis(data.analysis_id, job.id)
        application = await self._repo.add(
            job_id=job.id,
            analysis_id=data.analysis_id,
            platform=data.platform,
            status=data.status,
            salary_expectation=data.salary_expectation,
            next_step=data.next_step,
            applied_at=data.applied_at or date.today(),
        )
        application_id = application.id
        await self._commit()
        logger.info("application.created", application_id=str(application_id))
        return await self.get(application_id)

    async def list_all(self, *, statuses: Sequence[str] | None = None) -> list[Application]:
        return await self._repo.list_all(statuses=statuses)

    async def get(self, application_id: uuid.UUID) -> Application:
        application = await self._repo.get(application_id)
        if application is None:
            raise NotFoundError(APPLICATION_NOT_FOUND)
        return application

    async def update(self, application_id: uuid.UUID, data: ApplicationUpdate) -> Application:
        application = await self.get(application_id)
        changes = data.model_dump(exclude_unset=True)
        if changes.get("analysis_id") is not None:
            await self._check_analysis(changes["analysis_id"], application.job_id)
        for field, value in changes.items():
            setattr(application, field, value)
        await self._commit()
        logger.info(
            "application.updated", application_id=str(application_id), fields=sorted(changes)
        )
        self._session.expire(application)
        return await self.get(application_id)

    async def delete(self, application_id: uuid.UUID) -> None:
        await self._repo.delete(await self.get(application_id))
        await self._session.commit()

    async def _check_analysis(self, analysis_id: uuid.UUID | None, job_id: uuid.UUID) -> None:
        if analysis_id is None:
            return
        analysis = await AnalysisRepository(self._session, self._user_id).get(analysis_id)
        if analysis is None:
            raise NotFoundError(ANALYSIS_NOT_FOUND)
        if analysis.job_id != job_id:
            raise AppError(
                ANALYSIS_OTHER_JOB,
                code="invalid_analysis",
                status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            )

    async def _commit(self) -> None:
        try:
            await self._session.commit()
        except IntegrityError:
            # Duas criações simultâneas para a mesma vaga: a restrição única decide.
            await self._session.rollback()
            raise ConflictError(ALREADY_APPLIED) from None
