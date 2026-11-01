"""Rascunhos de resposta para perguntas de triagem, a partir de uma análise `done`.

Síncrono (uma chamada de LLM, com rate limit na rota). Mesma regra de honestidade da
análise: só trechos recuperados do currículo, citação literal validada no código, e o
que não tem evidência volta com `needs_user_input` + a pergunta para o candidato.
"""

import uuid
from http import HTTPStatus
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import EmbeddingProvider
from app.ai.llm import LLMOutputError, LLMProvider, structured_call
from app.ai.prompts import screening_request
from app.core.config import Settings
from app.core.errors import AppError, ConflictError, NotFoundError
from app.models.screening import ScreeningAnswer
from app.repositories.analyses import AnalysisRepository
from app.repositories.resumes import ResumeRepository
from app.repositories.screening import ScreeningRepository
from app.schemas.screening import LLMScreening, ScreeningRequest
from app.services.analysis import ANALYSIS_NOT_FOUND, RetrievedContext, check_quote, retrieve

logger = structlog.get_logger(__name__)

ANALYSIS_NOT_DONE = "A análise ainda não terminou. Espere o status `done` para gerar a triagem."


class AIInvalidOutputError(AppError):
    status_code = HTTPStatus.BAD_GATEWAY
    code = "ai_invalid_output"

    def __init__(self) -> None:
        super().__init__(
            "A IA devolveu respostas que não passaram na validação de evidências. Tente de novo."
        )


class _Validator:
    def __init__(self, ids: list[str], ctx: RetrievedContext) -> None:
        self._ids = ids
        self._ctx = ctx

    def __call__(self, output: LLMScreening) -> list[str]:
        problems: list[str] = []
        seen: list[str] = []
        for i, a in enumerate(output.answers):
            where = f"answers.{i} ({a.question_id})"
            if a.question_id not in self._ids:
                problems.append(f"{where}: pergunta inexistente")
                continue
            if a.question_id in seen:
                problems.append(f"{where}: pergunta repetida")
            seen.append(a.question_id)
            if a.needs_user_input:
                if not (a.user_question or "").strip():
                    problems.append(f"{where}: needs_user_input exige `user_question`")
            else:
                if not a.answer.strip():
                    problems.append(f"{where}: resposta vazia; use needs_user_input")
                if not a.evidence:
                    problems.append(f"{where}: resposta sem evidência; use needs_user_input")
            for j, ev in enumerate(a.evidence):
                problems.extend(check_quote(self._ctx, f"{where}.evidence.{j}", ev.chunk, ev.quote))
        missing = [qid for qid in self._ids if qid not in seen]
        if missing:
            problems.append(f"faltam respostas para: {', '.join(missing)}")
        return problems


class ScreeningService:
    def __init__(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
        settings: Settings,
        llm: LLMProvider,
        embeddings: EmbeddingProvider,
    ) -> None:
        self._session = session
        self._user_id = user_id
        self._settings = settings
        self._llm = llm
        self._embeddings = embeddings
        self._repo = ScreeningRepository(session, user_id)

    async def answer(self, analysis_id: uuid.UUID, data: ScreeningRequest) -> list[ScreeningAnswer]:
        analysis = await AnalysisRepository(self._session, self._user_id).get(analysis_id)
        if analysis is None:
            raise NotFoundError(ANALYSIS_NOT_FOUND)
        if analysis.status != "done":
            raise ConflictError(ANALYSIS_NOT_DONE)
        ids = [f"Q{i}" for i in range(1, len(data.questions) + 1)]
        ctx = await retrieve(
            ResumeRepository(self._session, self._user_id),
            self._embeddings,
            analysis.resume_id,
            list(zip(ids, data.questions, strict=True)),
            self._settings.analysis_top_k_chunks,
        )
        job_title = (analysis.result or {}).get("job", {}).get("title")
        request = screening_request(
            [
                {"id": qid, "text": text, "candidates": ctx.candidates[qid]}
                for qid, text in zip(ids, data.questions, strict=True)
            ],
            {alias: chunk.content for alias, chunk in ctx.chunks.items()},
            job_title,
        )
        log = logger.bind(analysis_id=str(analysis_id), questions=len(ids))
        try:
            output = await structured_call(self._llm, request, LLMScreening, _Validator(ids, ctx))
        except LLMOutputError as exc:
            log.warning("screening.invalid_output", problems=len(exc.problems))
            raise AIInvalidOutputError from None
        by_id = {a.question_id: a for a in output.answers}
        rows: list[dict[str, Any]] = []
        for ordinal, (qid, question) in enumerate(zip(ids, data.questions, strict=True)):
            a = by_id[qid]
            rows.append(
                {
                    "ordinal": ordinal,
                    "question": question,
                    "answer": a.answer.strip(),
                    "evidence": [
                        {"chunk_id": str(ctx.chunks[e.chunk].id), "quote": e.quote}
                        for e in a.evidence
                    ],
                    "needs_user_input": a.needs_user_input,
                    "user_question": a.user_question.strip()
                    if a.needs_user_input and a.user_question
                    else None,
                }
            )
        answers = await self._repo.add_many(analysis_id, rows)
        await self._session.commit()
        log.info("screening.done", needs_user_input=sum(1 for r in rows if r["needs_user_input"]))
        return answers

    async def list_for(self, analysis_id: uuid.UUID) -> list[ScreeningAnswer]:
        if await AnalysisRepository(self._session, self._user_id).get(analysis_id) is None:
            raise NotFoundError(ANALYSIS_NOT_FOUND)
        return await self._repo.list_for(analysis_id)
