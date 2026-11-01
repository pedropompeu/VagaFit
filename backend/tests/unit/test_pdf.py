import io

import pytest
from pypdf import PdfWriter

from app.services.pdf import InvalidPDFError, NotAPDFError, extract_pdf_text, looks_like_pdf
from tests.pdf_factory import make_pdf


async def _extract(data: bytes, *, max_pages: int = 10, limit_s: float = 5.0) -> str:
    return await extract_pdf_text(data, max_pages=max_pages, timeout_seconds=limit_s)


async def test_extracts_text() -> None:
    data = make_pdf([["EXPERIENCIA", "Dev Python (Acme) 2020-2024"], ["Formacao"]])
    text = await _extract(data)
    assert "Dev Python (Acme) 2020-2024" in text
    assert "Formacao" in text


def test_magic_number() -> None:
    assert looks_like_pdf(b"%PDF-1.7 ...")
    assert not looks_like_pdf(b"PK\x03\x04 docx")


async def test_rejects_non_pdf() -> None:
    with pytest.raises(NotAPDFError):
        await _extract(b"isto nao e um pdf")


async def test_rejects_too_many_pages() -> None:
    data = make_pdf([["pagina"]] * 3)
    with pytest.raises(InvalidPDFError, match="limite de 2"):
        await _extract(data, max_pages=2)


async def test_rejects_pdf_without_text() -> None:
    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    buffer = io.BytesIO()
    writer.write(buffer)
    with pytest.raises(InvalidPDFError, match="texto selecionável"):
        await _extract(buffer.getvalue())


async def test_rejects_encrypted_pdf() -> None:
    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    writer.encrypt("senha", algorithm="RC4-128")
    buffer = io.BytesIO()
    writer.write(buffer)
    with pytest.raises(InvalidPDFError, match="senha"):
        await _extract(buffer.getvalue())


async def test_rejects_corrupted_pdf() -> None:
    with pytest.raises(InvalidPDFError, match="Não foi possível ler"):
        await _extract(b"%PDF-1.4\nlixo sem estrutura")


async def test_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    import time

    import app.services.pdf as pdf_module

    def slow(data: bytes, max_pages: int) -> str:
        time.sleep(0.3)
        return "texto"

    monkeypatch.setattr(pdf_module, "_extract", slow)
    with pytest.raises(InvalidPDFError, match="demorou"):
        await _extract(make_pdf([["x"]]), limit_s=0.05)
