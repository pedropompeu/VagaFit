"""Regras de currículo: entrada (texto ou PDF), chunking, embeddings e CRUD do dono.

Log só com IDs e contagens. Nunca o texto do currículo.
"""

import uuid
from http import HTTPStatus

import structlog
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import EmbeddingProvider
from app.core.config import Settings
from app.core.errors import AppError, NotFoundError
from app.models.resume import Resume
from app.repositories.resumes import ResumeRepository, ResumeSummary
from app.schemas.resumes import ChunkPreview, ResumePreview
from app.services.chunking import chunk_resume, estimate_tokens
from app.services.pdf import extract_pdf_text
from app.services.text import normalize_document

logger = structlog.get_logger(__name__)

_READ_BLOCK = 64 * 1024


class PayloadTooLargeError(AppError):
    status_code = HTTPStatus.REQUEST_ENTITY_TOO_LARGE
    code = "payload_too_large"


class InvalidResumeInputError(AppError):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    code = "invalid_resume"


RESUME_NOT_FOUND = "Currículo não encontrado."


async def read_upload(file: UploadFile, *, max_bytes: int) -> bytes:
    """Lê o upload em blocos e para assim que passa do limite (não carrega 1 GB na memória)."""
    data = bytearray()
    while block := await file.read(_READ_BLOCK):
        data.extend(block)
        if len(data) > max_bytes:
            raise PayloadTooLargeError(
                f"O arquivo passa do limite de {max_bytes // (1024 * 1024)} MB."
            )
    return bytes(data)


class ResumeService:
    def __init__(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
        settings: Settings,
        embeddings: EmbeddingProvider,
    ) -> None:
        self._session = session
        self._user_id = user_id
        self._settings = settings
        self._embeddings = embeddings
        self._repo = ResumeRepository(session, user_id)

    async def resolve_text(self, *, text: str | None, file: UploadFile | None) -> str:
        """Exatamente uma fonte: texto colado ou PDF. Devolve o texto já normalizado."""
        if (text is None or not text.strip()) == (file is None):
            raise InvalidResumeInputError("Envie o texto do currículo ou um PDF (um dos dois).")
        if file is not None:
            data = await read_upload(file, max_bytes=self._settings.resume_max_upload_bytes)
            text = await extract_pdf_text(
                data,
                max_pages=self._settings.resume_max_pdf_pages,
                timeout_seconds=self._settings.pdf_extraction_timeout_seconds,
            )
        assert text is not None  # noqa: S101 - garantido pela checagem acima
        normalized = normalize_document(text)
        if not normalized:
            raise InvalidResumeInputError("O currículo está vazio.")
        if len(normalized) > self._settings.resume_max_text_chars:
            raise InvalidResumeInputError(
                f"O currículo passa do limite de {self._settings.resume_max_text_chars} caracteres."
            )
        return normalized

    @staticmethod
    def preview(text: str) -> ResumePreview:
        chunks = chunk_resume(text)
        return ResumePreview(
            chunk_count=len(chunks),
            chunks=[
                ChunkPreview(ordinal=i, content=c, estimated_tokens=estimate_tokens(c))
                for i, c in enumerate(chunks)
            ],
        )

    async def create(self, *, title: str, text: str) -> ResumeSummary:
        chunks = chunk_resume(text)
        vectors = await self._embeddings.embed(chunks)
        resume = await self._repo.add(
            title=title.strip(), raw_text=text, chunks=list(zip(chunks, vectors, strict=True))
        )
        await self._session.commit()
        logger.info(
            "resume.created",
            resume_id=str(resume.id),
            chunk_count=len(chunks),
            embedding_model=self._embeddings.model,
        )
        return ResumeSummary(resume=resume, chunk_count=len(chunks))

    async def list_all(self) -> list[ResumeSummary]:
        return await self._repo.list_all()

    async def get(self, resume_id: uuid.UUID) -> Resume:
        resume = await self._repo.get(resume_id, with_chunks=True)
        if resume is None:
            raise NotFoundError(RESUME_NOT_FOUND)
        return resume

    async def delete(self, resume_id: uuid.UUID) -> None:
        if not await self._repo.delete(resume_id):
            raise NotFoundError(RESUME_NOT_FOUND)
        await self._session.commit()
        logger.info("resume.deleted", resume_id=str(resume_id))
