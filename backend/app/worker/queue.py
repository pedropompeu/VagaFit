"""Fila de tarefas atrás de um Protocol. A API enfileira; o teste troca por uma fila em memória
(o CI não tem Redis e nenhum teste de API deve depender do worker)."""

from typing import Protocol

from app.worker.celery_app import celery_app

EXTRACT_JOB_TASK = "vagafit.extract_job"
RUN_ANALYSIS_TASK = "vagafit.run_analysis"


class TaskQueue(Protocol):
    def enqueue(self, task_name: str, *args: str) -> None: ...


class CeleryTaskQueue:
    def enqueue(self, task_name: str, *args: str) -> None:
        celery_app.send_task(task_name, args=list(args))


class InMemoryTaskQueue:
    """Só para teste: guarda o que seria enfileirado."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, tuple[str, ...]]] = []

    def enqueue(self, task_name: str, *args: str) -> None:
        self.sent.append((task_name, args))
