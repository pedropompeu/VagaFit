"""Painel de candidaturas: CRUD com filtro por status."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Query, Response, status

from app.api.deps import ApplicationServiceDep
from app.core.errors import ErrorResponse
from app.schemas.applications import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationStatus,
    ApplicationUpdate,
)

router = APIRouter(prefix="/applications", tags=["applications"])

_ERR_404: dict[int | str, dict[str, Any]] = {
    404: {"model": ErrorResponse, "description": "Não encontrada"}
}


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Registrar candidatura",
    description=(
        "Uma candidatura por vaga. `analysis_id` é opcional e precisa ser uma análise da "
        "mesma vaga. Status em código: `sent`, `in_review`, `tech_test`, `interview`, "
        "`offer`, `rejected`, `no_response`."
    ),
    responses={
        404: {"model": ErrorResponse, "description": "Vaga ou análise não encontrada"},
        409: {"model": ErrorResponse, "description": "Já existe candidatura para a vaga"},
    },
)
async def create_application(
    body: ApplicationCreate, service: ApplicationServiceDep
) -> ApplicationRead:
    return ApplicationRead.model_validate(await service.create(body))


@router.get(
    "",
    summary="Listar candidaturas",
    description=(
        "Mais recentes primeiro (data da candidatura). Filtro: `?status=sent&status=interview`."
    ),
)
async def list_applications(
    service: ApplicationServiceDep,
    status_filter: Annotated[
        list[ApplicationStatus] | None, Query(alias="status", description="Um ou mais status.")
    ] = None,
) -> list[ApplicationRead]:
    return [
        ApplicationRead.model_validate(a) for a in await service.list_all(statuses=status_filter)
    ]


@router.get("/{application_id}", summary="Detalhar candidatura", responses=_ERR_404)
async def get_application(
    application_id: uuid.UUID, service: ApplicationServiceDep
) -> ApplicationRead:
    return ApplicationRead.model_validate(await service.get(application_id))


@router.patch(
    "/{application_id}",
    summary="Atualizar candidatura",
    description="Atualização parcial: só os campos enviados mudam (`null` limpa os opcionais).",
    responses=_ERR_404,
)
async def update_application(
    application_id: uuid.UUID, body: ApplicationUpdate, service: ApplicationServiceDep
) -> ApplicationRead:
    return ApplicationRead.model_validate(await service.update(application_id, body))


@router.delete(
    "/{application_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Apagar candidatura",
    responses=_ERR_404,
)
async def delete_application(application_id: uuid.UUID, service: ApplicationServiceDep) -> Response:
    await service.delete(application_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
