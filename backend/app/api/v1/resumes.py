"""Rotas de currículo. Entrada multipart: texto colado (`text`) ou PDF (`file`)."""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, File, Form, Request, Response, UploadFile, status

from app.api.deps import ResumeServiceDep
from app.core.errors import ErrorResponse
from app.core.rate_limit import rate_limit
from app.schemas.resumes import ResumeChunkRead, ResumeDetail, ResumePreview, ResumeRead

router = APIRouter(prefix="/resumes", tags=["resumes"])

_OpenAPIResponses = dict[int | str, dict[str, Any]]

_ERR_404: _OpenAPIResponses = {404: {"model": ErrorResponse, "description": "Não encontrado"}}
_ERR_INPUT: _OpenAPIResponses = {
    413: {"model": ErrorResponse, "description": "Arquivo acima de 5 MB"},
    415: {"model": ErrorResponse, "description": "Arquivo não é PDF"},
    422: {"model": ErrorResponse, "description": "Texto vazio, PDF ilegível ou sem texto"},
    429: {"model": ErrorResponse, "description": "Muitas requisições"},
}

TextField = Annotated[
    str | None,
    Form(description="Texto do currículo colado. Use isto ou `file`.", max_length=60_000),
]
FileField = Annotated[
    UploadFile | None, File(description="PDF do currículo (até 5 MB). Use isto ou `text`.")
]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Enviar currículo",
    description=(
        "Recebe o texto colado ou um PDF, divide em chunks estruturais e gera os embeddings. "
        "Limite: 10/min por IP."
    ),
    responses=_ERR_INPUT,
)
@rate_limit("10/minute")
async def create_resume(
    request: Request,
    service: ResumeServiceDep,
    title: Annotated[str, Form(min_length=1, max_length=120, examples=["Currículo backend 2026"])],
    text: TextField = None,
    file: FileField = None,
) -> ResumeRead:
    content = await service.resolve_text(text=text, file=file)
    created = await service.create(title=title, text=content)
    return ResumeRead(
        id=created.resume.id,
        title=created.resume.title,
        created_at=created.resume.created_at,
        chunk_count=created.chunk_count,
    )


@router.post(
    "/preview",
    summary="Pré-visualizar chunks",
    description="Mostra como o currículo será dividido. Não salva e não gera embedding.",
    responses=_ERR_INPUT,
)
@rate_limit("30/minute")
async def preview_resume(
    request: Request,
    service: ResumeServiceDep,
    text: TextField = None,
    file: FileField = None,
) -> ResumePreview:
    content = await service.resolve_text(text=text, file=file)
    return service.preview(content)


@router.get(
    "", summary="Listar currículos", description="Currículos do usuário, mais novos primeiro."
)
async def list_resumes(service: ResumeServiceDep) -> list[ResumeRead]:
    return [
        ResumeRead(
            id=s.resume.id,
            title=s.resume.title,
            created_at=s.resume.created_at,
            chunk_count=s.chunk_count,
        )
        for s in await service.list_all()
    ]


@router.get(
    "/{resume_id}",
    summary="Detalhar currículo",
    description="Texto normalizado e chunks (com `id`, usado como evidência nas análises).",
    responses=_ERR_404,
)
async def get_resume(resume_id: uuid.UUID, service: ResumeServiceDep) -> ResumeDetail:
    resume = await service.get(resume_id)
    return ResumeDetail(
        id=resume.id,
        title=resume.title,
        created_at=resume.created_at,
        raw_text=resume.raw_text,
        chunks=[ResumeChunkRead.model_validate(c) for c in resume.chunks],
    )


@router.delete(
    "/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Apagar currículo",
    description="Apaga o currículo e os chunks.",
    responses=_ERR_404,
)
async def delete_resume(resume_id: uuid.UUID, service: ResumeServiceDep) -> Response:
    await service.delete(resume_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
