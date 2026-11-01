"""Extração de texto de PDF. A leitura é bloqueante: roda em threadpool, com timeout."""

import asyncio
import io
from http import HTTPStatus

from pypdf import PdfReader
from pypdf.errors import PdfReadError
from starlette.concurrency import run_in_threadpool

from app.core.errors import AppError

PDF_MAGIC = b"%PDF-"


class InvalidPDFError(AppError):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    code = "invalid_pdf"


class NotAPDFError(AppError):
    status_code = HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    code = "unsupported_media_type"

    def __init__(self) -> None:
        super().__init__("Envie um arquivo PDF.")


def looks_like_pdf(data: bytes) -> bool:
    return data[:1024].lstrip().startswith(PDF_MAGIC)


def _extract(data: bytes, max_pages: int) -> str:
    try:
        reader = PdfReader(io.BytesIO(data))
        if reader.is_encrypted:
            raise InvalidPDFError("PDF protegido por senha não é aceito.")
        if len(reader.pages) > max_pages:
            raise InvalidPDFError(f"O PDF passa do limite de {max_pages} páginas.")
        pages = [page.extract_text() or "" for page in reader.pages]
    except InvalidPDFError:
        raise
    except (PdfReadError, ValueError, KeyError, TypeError) as exc:
        raise InvalidPDFError("Não foi possível ler o PDF.") from exc
    return "\n\n".join(pages)


async def extract_pdf_text(data: bytes, *, max_pages: int, timeout_seconds: float) -> str:
    """Valida o magic number e extrai o texto. PDF sem texto (escaneado) é recusado."""
    if not looks_like_pdf(data):
        raise NotAPDFError()
    try:
        text = await asyncio.wait_for(run_in_threadpool(_extract, data, max_pages), timeout_seconds)
    except TimeoutError as exc:
        raise InvalidPDFError("A leitura do PDF demorou demais.") from exc
    if not text.strip():
        raise InvalidPDFError(
            "O PDF não tem texto selecionável (talvez seja escaneado). Cole o texto do currículo."
        )
    return text
