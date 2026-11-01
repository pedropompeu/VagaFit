"""Rotas de análise. `POST` responde 202 e o worker processa; o front acompanha pelo `GET`."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Query, Request, status

from app.api.deps import AnalysisServiceDep
from app.core.errors import ErrorResponse
from app.core.rate_limit import rate_limit
from app.models.analysis import Analysis
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisCreated,
    AnalysisDetail,
    AnalysisRead,
    AnalysisResult,
)

router = APIRouter(prefix="/analyses", tags=["analyses"])

_ERR_404: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Não encontrada"}
}


def _read(analysis: Analysis) -> AnalysisRead:
    return AnalysisRead.model_validate(analysis)


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Pedir análise",
    description=(
        "Enfileira a análise do currículo contra a vaga. Se já existe uma análise igual "
        "(mesmo texto, modelo e versão do prompt) pronta ou em andamento, devolve essa "
        "(`reused: true`) sem gastar outra chamada de IA. Limite: 10/min por IP."
    ),
    responses={
        404: {"model": ErrorResponse, "description": "Currículo ou vaga não encontrados"},
        429: {"model": ErrorResponse, "description": "Muitas requisições"},
    },
)
@rate_limit("10/minute")
async def create_analysis(
    request: Request, body: AnalysisCreate, service: AnalysisServiceDep
) -> AnalysisCreated:
    created = await service.create(body)
    return AnalysisCreated(**_read(created.analysis).model_dump(), reused=created.reused)


@router.get("", summary="Listar análises", description="Mais novas primeiro, sem o resultado.")
async def list_analyses(
    service: AnalysisServiceDep,
    job_id: Annotated[uuid.UUID | None, Query(description="Só as desta vaga.")] = None,
) -> list[AnalysisRead]:
    return [_read(a) for a in await service.list_all(job_id=job_id)]


@router.get(
    "/{analysis_id}",
    summary="Detalhar análise",
    description="Status e, quando `done`, score, requisitos com evidência, lacunas e sugestões.",
    responses=_ERR_404,
)
async def get_analysis(analysis_id: uuid.UUID, service: AnalysisServiceDep) -> AnalysisDetail:
    analysis = await service.get(analysis_id)
    return AnalysisDetail(
        **_read(analysis).model_dump(),
        result=AnalysisResult.model_validate(analysis.result) if analysis.result else None,
    )
