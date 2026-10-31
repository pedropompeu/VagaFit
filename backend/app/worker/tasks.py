"""Tasks do worker. A análise de vaga chega na fase 4."""

from app.worker.celery_app import celery_app


@celery_app.task(name="vagafit.ping")
def ping() -> str:
    """Smoke test do worker: `celery -A app.worker.celery_app call vagafit.ping`."""
    return "pong"
