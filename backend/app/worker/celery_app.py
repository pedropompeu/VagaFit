"""Aplicação Celery. Broker e backend no Redis."""

from celery import Celery

from app.core.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "vagafit",
    broker=_settings.redis_url,
    backend=_settings.redis_url,
    include=["app.worker.tasks"],
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,  # tarefa só sai da fila depois de concluída
    worker_prefetch_multiplier=1,  # análises são longas; não acumular no mesmo worker
    task_reject_on_worker_lost=True,
    result_expires=60 * 60 * 24,
    timezone="UTC",
)
