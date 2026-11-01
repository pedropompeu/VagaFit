"""Tasks do worker. Cada task roda o código async em `run_async` (engine próprio, NullPool)
e cria o cliente de IA dentro do loop da task (cliente httpx fica preso ao loop)."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm import build_llm_provider
from app.core.config import get_settings
from app.services.job_extraction import run_extraction_task
from app.worker.celery_app import celery_app
from app.worker.queue import EXTRACT_JOB_TASK
from app.worker.runtime import run_async


@celery_app.task(name="vagafit.ping")
def ping() -> str:
    """Smoke test do worker: `celery -A app.worker.celery_app call vagafit.ping`."""
    return "pong"


@celery_app.task(name=EXTRACT_JOB_TASK)
def extract_job(job_id: str, user_id: str) -> bool:
    async def job(session: AsyncSession) -> bool:
        llm = build_llm_provider(get_settings())
        try:
            return await run_extraction_task(session, uuid.UUID(user_id), uuid.UUID(job_id), llm)
        finally:
            await llm.aclose()

    return run_async(job)
