"""Extração de requisitos da vaga com LLM (saída estruturada e validada).

Os IDs (`R1`, `R2`...) são atribuídos aqui, na ordem em que o modelo devolveu, para que
as análises citem requisitos por um ID estável. Log só com IDs e contagens.
"""

import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.errors import AIProviderError
from app.ai.llm import LLMOutputError, LLMProvider, structured_call
from app.ai.prompts import PROMPT_VERSION, extract_requirements_request
from app.models.job import Job
from app.repositories.jobs import JobRepository
from app.schemas.extraction import JobExtraction, LLMJobExtraction, Requirement
from app.services.text import normalize_for_match

logger = structlog.get_logger(__name__)


def _check_extraction(extraction: LLMJobExtraction) -> list[str]:
    problems = []
    seen: set[str] = set()
    for index, req in enumerate(extraction.requirements):
        key = normalize_for_match(req.text)
        if not key:
            problems.append(f"requirements.{index}: texto vazio")
        elif key in seen:
            problems.append(f"requirements.{index}: requisito repetido")
        seen.add(key)
    return problems


async def extract_requirements(llm: LLMProvider, job_text: str) -> JobExtraction:
    parsed = await structured_call(
        llm, extract_requirements_request(job_text), LLMJobExtraction, _check_extraction
    )
    return JobExtraction(
        title=parsed.title,
        company=parsed.company,
        seniority=parsed.seniority,
        work_model=parsed.work_model,
        location=parsed.location,
        stack=list(dict.fromkeys(parsed.stack)),
        requirements=[
            Requirement(id=f"R{i}", text=r.text.strip(), kind=r.kind)
            for i, r in enumerate(parsed.requirements, start=1)
        ],
        model=llm.model,
        prompt_version=PROMPT_VERSION,
    )


async def ensure_extracted(
    session: AsyncSession, user_id: uuid.UUID, job_id: uuid.UUID, llm: LLMProvider
) -> JobExtraction | None:
    """Extrai e salva se ainda não houver extração. Devolve a extração (nova ou existente).

    `None` quando a vaga não existe (ou não é do usuário). Erros de LLM sobem para quem
    chamou decidir (a task de extração engole e loga; a análise marca `failed`).
    """
    repo = JobRepository(session, user_id)
    job = await repo.get(job_id)
    if job is None:
        return None
    if job.extracted is not None:
        return JobExtraction.model_validate(job.extracted)
    extraction = await extract_requirements(llm, job.raw_text)
    await _save(repo, job, extraction)
    await session.commit()
    logger.info(
        "job.extracted",
        job_id=str(job_id),
        requirements=len(extraction.requirements),
        model=extraction.model,
    )
    return extraction


async def _save(repo: JobRepository, job: Job, extraction: JobExtraction) -> None:
    await repo.set_extracted(job, extraction.model_dump(mode="json"))


async def run_extraction_task(
    session: AsyncSession, user_id: uuid.UUID, job_id: uuid.UUID, llm: LLMProvider
) -> bool:
    """Corpo da task `vagafit.extract_job`. Falha de IA não derruba o worker: a vaga fica
    `pending` e a análise tenta extrair de novo quando for pedida."""
    try:
        return await ensure_extracted(session, user_id, job_id, llm) is not None
    except (LLMOutputError, AIProviderError) as exc:
        logger.warning("job.extraction_failed", job_id=str(job_id), error=type(exc).__name__)
        return False
