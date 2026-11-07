"""Rotas de vagas. A extração de requisitos roda no worker (`extraction_status`)."""

import uuid
from typing import Any

from fastapi import APIRouter, Request, Response, status

from app.api.deps import JobServiceDep
from app.core.errors import ErrorResponse
from app.core.rate_limit import rate_limit
from app.models.job import Job
from app.schemas.extraction import JobExtraction
from app.schemas.jobs import JobCreate, JobDetail, JobRead

router = APIRouter(prefix="/jobs", tags=["jobs"])

_ERR_404: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Não encontrada"}
}


def _read(job: Job) -> JobRead:
    return JobRead(
        id=job.id,
        title=job.title,
        company=job.company,
        created_at=job.created_at,
        extraction_status=_status(job),
    )


def _status(job: Job) -> str:
    if job.extracted is not None:
        return "done"
    return "failed" if job.extraction_error else "pending"


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar vaga",
    description=(
        "Salva o texto da vaga e enfileira a extração de requisitos (assíncrona). "
        "Limite: 10/min por IP."
    ),
    responses={429: {"model": ErrorResponse, "description": "Muitas requisições"}},
)
@rate_limit("10/minute")
async def create_job(request: Request, body: JobCreate, service: JobServiceDep) -> JobRead:
    return _read(await service.create(body))


@router.get("", summary="Listar vagas", description="Vagas do usuário, mais novas primeiro.")
async def list_jobs(service: JobServiceDep) -> list[JobRead]:
    return [_read(job) for job in await service.list_all()]


@router.get(
    "/{job_id}",
    summary="Detalhar vaga",
    description="Texto da vaga e requisitos extraídos (`null` enquanto `pending`).",
    responses=_ERR_404,
)
async def get_job(job_id: uuid.UUID, service: JobServiceDep) -> JobDetail:
    job = await service.get(job_id)
    return JobDetail(
        **_read(job).model_dump(),
        raw_text=job.raw_text,
        extracted=JobExtraction.model_validate(job.extracted) if job.extracted else None,
    )


@router.post(
    "/{job_id}/extract",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Tentar a extração de novo",
    description=(
        "Reenfileira a extração de uma vaga em `failed`. Vaga já extraída é devolvida sem mudança. "
        "Limite: 10/min por IP."
    ),
    responses={**_ERR_404, 429: {"model": ErrorResponse, "description": "Muitas requisições"}},
)
@rate_limit("10/minute")
async def retry_extraction(request: Request, job_id: uuid.UUID, service: JobServiceDep) -> JobRead:
    return _read(await service.retry_extraction(job_id))


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Apagar vaga",
    responses=_ERR_404,
)
async def delete_job(job_id: uuid.UUID, service: JobServiceDep) -> Response:
    await service.delete(job_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
