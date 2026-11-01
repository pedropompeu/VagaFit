"""Análise de aderência: pedido pela API (com cache por hash) e execução no worker.

Fluxo do worker: extrair requisitos (se faltar) -> 3 trechos mais próximos por requisito
(pgvector) -> veredito do LLM citando só os trechos recebidos -> validação no código
(trecho existe, é deste currículo e a citação é literal) -> lacunas, sugestões e score
calculados no código -> `done` ou `failed` com mensagem clara.

Log só com IDs, contagens e nomes de erro. Nunca texto de currículo, vaga ou resposta.
"""

import hashlib
import json
import uuid
from dataclasses import dataclass
from datetime import timedelta

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import EmbeddingProvider
from app.ai.errors import AIProviderError
from app.ai.llm import LLMOutputError, LLMProvider, structured_call
from app.ai.prompts import PROMPT_VERSION, analyze_fit_request
from app.core.config import Settings
from app.core.errors import NotFoundError
from app.models.analysis import Analysis
from app.models.mixins import utcnow
from app.models.resume import ResumeChunk
from app.repositories.analyses import AnalysisRepository
from app.repositories.jobs import JobRepository
from app.repositories.resumes import ResumeRepository
from app.schemas.analysis import (
    AnalysisCreate,
    AnalysisResult,
    Evidence,
    Gap,
    JobSummary,
    LLMAnalysis,
    RequirementResult,
    Suggestion,
)
from app.schemas.extraction import JobExtraction
from app.services.job_extraction import ensure_extracted
from app.services.jobs import JOB_NOT_FOUND
from app.services.resumes import RESUME_NOT_FOUND
from app.services.scoring import compute_score
from app.services.text import quote_in_text
from app.worker.queue import RUN_ANALYSIS_TASK, TaskQueue

logger = structlog.get_logger(__name__)

ANALYSIS_NOT_FOUND = "Análise não encontrada."
MSG_AI_UNAVAILABLE = "O serviço de IA está indisponível. Tente de novo em alguns minutos."
MSG_INVALID_OUTPUT = (
    "A IA devolveu uma resposta que não passou na validação de evidências duas vezes. "
    "Tente de novo."
)
MSG_MISSING_INPUT = "O currículo ou a vaga desta análise não existe mais."
MSG_INTERNAL = "Erro interno ao processar a análise."


def input_hash(resume_text: str, job_text: str, settings: Settings) -> str:
    """SHA-256 de (currículo, vaga) + modelos + versão do prompt + k.

    Mudar modelo ou prompt muda o hash: resultado antigo não é reaproveitado.
    """
    material = json.dumps(
        [
            resume_text,
            job_text,
            settings.llm_model_id,
            settings.embedding_model_id,
            PROMPT_VERSION,
            settings.analysis_top_k_chunks,
        ],
        ensure_ascii=False,
    )
    return hashlib.sha256(material.encode()).hexdigest()


@dataclass(frozen=True)
class CreatedAnalysis:
    analysis: Analysis
    reused: bool


class AnalysisService:
    """Lado da API: pedir, listar e ler análises do dono."""

    def __init__(
        self,
        session: AsyncSession,
        user_id: uuid.UUID,
        settings: Settings,
        queue: TaskQueue,
    ) -> None:
        self._session = session
        self._user_id = user_id
        self._settings = settings
        self._queue = queue
        self._repo = AnalysisRepository(session, user_id)

    async def create(self, data: AnalysisCreate) -> CreatedAnalysis:
        resume = await ResumeRepository(self._session, self._user_id).get(data.resume_id)
        if resume is None:
            raise NotFoundError(RESUME_NOT_FOUND)
        job = await JobRepository(self._session, self._user_id).get(data.job_id)
        if job is None:
            raise NotFoundError(JOB_NOT_FOUND)
        digest = input_hash(resume.raw_text, job.raw_text, self._settings)
        stale = timedelta(minutes=self._settings.analysis_stale_after_minutes)
        existing = await self._repo.find_reusable(
            resume_id=resume.id,
            job_id=job.id,
            input_hash=digest,
            active_since=utcnow() - stale,
        )
        if existing is not None:
            logger.info("analysis.reused", analysis_id=str(existing.id), status=existing.status)
            return CreatedAnalysis(existing, reused=True)
        analysis = await self._repo.add(resume_id=resume.id, job_id=job.id, input_hash=digest)
        await self._session.commit()
        self._queue.enqueue(RUN_ANALYSIS_TASK, str(analysis.id), str(self._user_id))
        logger.info("analysis.requested", analysis_id=str(analysis.id))
        return CreatedAnalysis(analysis, reused=False)

    async def list_all(self, *, job_id: uuid.UUID | None = None) -> list[Analysis]:
        return await self._repo.list_all(job_id=job_id)

    async def get(self, analysis_id: uuid.UUID) -> Analysis:
        analysis = await self._repo.get(analysis_id)
        if analysis is None:
            raise NotFoundError(ANALYSIS_NOT_FOUND)
        return analysis


# --- worker ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Context:
    """O que foi mandado ao LLM: alias -> chunk, e candidatos por requisito."""

    chunks: dict[str, ResumeChunk]
    candidates: dict[str, list[str]]


def _validate(extraction: JobExtraction, ctx: _Context) -> "_Validator":
    return _Validator(extraction, ctx)


class _Validator:
    def __init__(self, extraction: JobExtraction, ctx: _Context) -> None:
        self._expected = [r.id for r in extraction.requirements]
        self._ctx = ctx

    def __call__(self, output: LLMAnalysis) -> list[str]:
        problems: list[str] = []
        seen: list[str] = []
        for i, v in enumerate(output.verdicts):
            where = f"verdicts.{i} ({v.requirement_id})"
            if v.requirement_id not in self._expected:
                problems.append(f"{where}: requisito inexistente")
                continue
            if v.requirement_id in seen:
                problems.append(f"{where}: requisito repetido")
            seen.append(v.requirement_id)
            if v.verdict != "not_met" and not v.evidence:
                problems.append(f"{where}: `{v.verdict}` exige evidência; use not_met")
            if v.verdict == "not_met":
                continue
            for j, ev in enumerate(v.evidence):
                problems.extend(self._check_quote(f"{where}.evidence.{j}", ev.chunk, ev.quote))
        missing = [rid for rid in self._expected if rid not in seen]
        if missing:
            problems.append(f"faltam vereditos para: {', '.join(missing)}")
        for k, s in enumerate(output.suggestions):
            problems.extend(self._check_quote(f"suggestions.{k}", s.chunk, s.original))
        return problems

    def _check_quote(self, where: str, alias: str, quote: str) -> list[str]:
        chunk = self._ctx.chunks.get(alias)
        if chunk is None:
            return [f"{where}: trecho {alias} não foi enviado; cite só os recebidos"]
        if not quote_in_text(quote, chunk.content):
            return [f"{where}: a citação não é cópia literal do trecho {alias}"]
        return []


def build_result(
    extraction: JobExtraction, ctx: _Context, output: LLMAnalysis, model: str
) -> AnalysisResult:
    """Monta o resultado só com saída já validada. Lacunas e score saem do código."""
    by_id = {v.requirement_id: v for v in output.verdicts}
    requirements = []
    for req in extraction.requirements:
        v = by_id[req.id]
        evidence = (
            []
            if v.verdict == "not_met"
            else [Evidence(chunk_id=ctx.chunks[e.chunk].id, quote=e.quote) for e in v.evidence]
        )
        requirements.append(
            RequirementResult(
                id=req.id,
                text=req.text,
                kind=req.kind,
                verdict=v.verdict,
                evidence=evidence,
                rationale=v.rationale,
            )
        )
    score, breakdown = compute_score(requirements)
    return AnalysisResult(
        score=score,
        breakdown=breakdown,
        job=JobSummary(
            title=extraction.title,
            seniority=extraction.seniority,
            work_model=extraction.work_model,
            stack=extraction.stack,
        ),
        requirements=requirements,
        gaps=[
            Gap(requirement_id=r.id, text=r.text, kind=r.kind, verdict=r.verdict)
            for r in requirements
            if r.verdict != "met"
        ],
        suggestions=[
            Suggestion(
                chunk_id=ctx.chunks[s.chunk].id, original=s.original, suggestion=s.suggestion
            )
            for s in output.suggestions
        ],
        model=model,
        prompt_version=PROMPT_VERSION,
    )


class AnalysisRunner:
    """Lado do worker. Testável com sessão de teste e provedores falsos."""

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
        self._repo = AnalysisRepository(session, user_id)

    async def run(self, analysis_id: uuid.UUID) -> str | None:
        """Executa e devolve o status final (`None` se a análise não existe)."""
        analysis = await self._repo.get(analysis_id)
        if analysis is None:
            logger.warning("analysis.missing", analysis_id=str(analysis_id))
            return None
        if analysis.status in ("done", "failed"):
            return analysis.status
        analysis.status = "running"
        await self._session.commit()
        log = logger.bind(analysis_id=str(analysis_id))
        try:
            result = await self._analyze(analysis)
        except AIProviderError:
            return await self._fail(analysis_id, MSG_AI_UNAVAILABLE, "ai_unavailable")
        except LLMOutputError as exc:
            log.warning("analysis.invalid_output", task=exc.task, problems=len(exc.problems))
            return await self._fail(analysis_id, MSG_INVALID_OUTPUT, "invalid_output")
        except _MissingInputError:
            return await self._fail(analysis_id, MSG_MISSING_INPUT, "missing_input")
        except Exception as exc:
            log.error("analysis.crashed", error=type(exc).__name__)
            return await self._fail(analysis_id, MSG_INTERNAL, "internal")
        analysis.status = "done"
        analysis.score = result.score
        analysis.result = result.model_dump(mode="json")
        analysis.error = None
        analysis.finished_at = utcnow()
        await self._session.commit()
        log.info(
            "analysis.done",
            score=result.score,
            requirements=len(result.requirements),
            gaps=len(result.gaps),
            model=result.model,
        )
        return "done"

    async def _analyze(self, analysis: Analysis) -> AnalysisResult:
        extraction = await ensure_extracted(
            self._session, self._user_id, analysis.job_id, self._llm
        )
        if extraction is None:
            raise _MissingInputError
        ctx = await self._retrieve(analysis.resume_id, extraction)
        request = analyze_fit_request(
            [
                {"id": r.id, "text": r.text, "kind": r.kind, "candidates": ctx.candidates[r.id]}
                for r in extraction.requirements
            ],
            {alias: chunk.content for alias, chunk in ctx.chunks.items()},
        )
        output = await structured_call(self._llm, request, LLMAnalysis, _validate(extraction, ctx))
        return build_result(extraction, ctx, output, self._llm.model)

    async def _retrieve(self, resume_id: uuid.UUID, extraction: JobExtraction) -> _Context:
        resumes = ResumeRepository(self._session, self._user_id)
        if await resumes.get(resume_id) is None:
            raise _MissingInputError
        vectors = await self._embeddings.embed([r.text for r in extraction.requirements])
        aliases: dict[uuid.UUID, str] = {}
        chunks: dict[str, ResumeChunk] = {}
        candidates: dict[str, list[str]] = {}
        for req, vector in zip(extraction.requirements, vectors, strict=True):
            matches = await resumes.nearest_chunks(
                resume_id, vector, k=self._settings.analysis_top_k_chunks
            )
            names = []
            for match in matches:
                alias = aliases.get(match.chunk.id)
                if alias is None:
                    alias = f"C{len(aliases) + 1}"
                    aliases[match.chunk.id] = alias
                    chunks[alias] = match.chunk
                names.append(alias)
            candidates[req.id] = names
        return _Context(chunks=chunks, candidates=candidates)

    async def _fail(self, analysis_id: uuid.UUID, message: str, reason: str) -> str:
        await self._session.rollback()
        analysis = await self._repo.get(analysis_id)
        if analysis is None:
            return "failed"
        analysis.status = "failed"
        analysis.error = message
        analysis.finished_at = utcnow()
        await self._session.commit()
        logger.warning("analysis.failed", analysis_id=str(analysis_id), reason=reason)
        return "failed"


class _MissingInputError(Exception):
    """Currículo ou vaga apagados entre o pedido e a execução."""
