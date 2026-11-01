"""Dados de exemplo para a demo: `make seed` (ou `python -m app.seed [--reset]`).

Tudo aqui é FICTÍCIO: pessoa, empresas, vagas e e-mail (domínio reservado `.example`).
Nunca coloque currículo real neste arquivo, porque ele é versionado.

O seed roda o fluxo completo dentro do processo, sem o worker: cria a conta, o currículo
(chunking e embeddings), duas vagas (extração), as análises, uma triagem e uma candidatura.
Usa os provedores configurados. Com o padrão `fake` não chama nenhuma API externa; com
`anthropic` ou `openai` gasta crédito, e o script avisa antes. Em produção, recusa.
"""

import argparse
import asyncio
import sys
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.embeddings import EmbeddingProvider, build_embedding_provider
from app.ai.llm import LLMProvider, build_llm_provider
from app.core.config import Settings, get_settings
from app.db.session import build_engine, build_sessionmaker
from app.repositories.users import UserRepository
from app.schemas.analysis import AnalysisCreate
from app.schemas.applications import ApplicationCreate
from app.schemas.jobs import JobCreate
from app.schemas.screening import ScreeningRequest
from app.services.analysis import AnalysisRunner, AnalysisService
from app.services.applications import ApplicationService
from app.services.auth import AuthService
from app.services.job_extraction import run_extraction_task
from app.services.jobs import JobService
from app.services.resumes import ResumeService
from app.services.screening import ScreeningService
from app.worker.queue import InMemoryTaskQueue

DEMO_EMAIL = "demo@vagafit.example"
# Senha só da conta de demonstração local. O seed recusa rodar em produção.
DEMO_PASSWORD = "demo-vagafit-123"  # noqa: S105

RESUME_TITLE = "Currículo fictício: Ana Exemplo"
RESUME_TEXT = """\
Ana Exemplo
Pessoa desenvolvedora backend (perfil fictício para demonstração do VagaFit)

RESUMO
Desenvolvedora backend com 6 anos de experiência em Python, APIs REST e bancos relacionais.

EXPERIÊNCIA
Empresa Fictícia de Pagamentos Ltda. | Desenvolvedora Backend Sênior | 2022 a 2026
- Construí APIs REST em Python com FastAPI para conciliação de pagamentos.
- Modelei o banco PostgreSQL e escrevi migrações com Alembic.
- Coloquei filas assíncronas com Celery e Redis para o processamento de lotes.
- Escrevi testes automatizados com pytest e mantive a cobertura acima de 85%.

Loja Imaginária S.A. | Desenvolvedora Backend Pleno | 2020 a 2022
- Mantive serviços em Django e integrações com APIs de frete.
- Empacotei os serviços com Docker e configurei pipelines de CI no GitHub Actions.

FORMAÇÃO
Bacharelado em Sistemas de Informação, Universidade Exemplo, 2019.

IDIOMAS
Inglês intermediário.
"""

JOBS = (
    JobCreate(
        title="Pessoa Desenvolvedora Backend Python Sênior",
        company="Empresa Exemplo S.A.",
        raw_text="""\
Pessoa Desenvolvedora Backend Python Sênior
Empresa: Empresa Exemplo S.A. (vaga fictícia)
Modelo: remoto.

Requisitos:
- Experiência com Python e FastAPI
- PostgreSQL e migrações com Alembic
- Filas com Celery e Redis
- Testes automatizados com pytest
- Kubernetes em produção

Diferenciais:
- Docker e GitHub Actions
- Inglês avançado
""",
    ),
    JobCreate(
        title="Pessoa Engenheira de Dados Pleno",
        company="Dados Inventados Ltda.",
        raw_text="""\
Pessoa Engenheira de Dados Pleno
Empresa: Dados Inventados Ltda. (vaga fictícia)
Modelo: híbrido.

Requisitos:
- Python para pipelines de dados
- Apache Spark
- Airflow para orquestração

Diferenciais:
- PostgreSQL
""",
    ),
)

SCREENING_QUESTIONS = [
    "Você tem experiência com filas assíncronas?",
    "Já trabalhou com Kubernetes em produção?",
]


@dataclass
class SeedReport:
    created: bool
    analyses: list[tuple[str, str | None, int | None]] = field(default_factory=list)
    screening_needs_input: int = 0


class SeedRefusedError(RuntimeError):
    pass


async def seed(
    session: AsyncSession,
    settings: Settings,
    llm: LLMProvider,
    embeddings: EmbeddingProvider,
    *,
    reset: bool = False,
) -> SeedReport:
    if settings.environment == "production":
        raise SeedRefusedError("O seed não roda em produção.")

    users = UserRepository(session)
    existing = await users.get_by_email(DEMO_EMAIL)
    if existing is not None:
        if not reset:
            return SeedReport(created=False)
        await users.delete(existing.id)  # cascata apaga currículos, vagas e análises
        await session.commit()

    auth = await AuthService(session, settings).register(email=DEMO_EMAIL, password=DEMO_PASSWORD)
    user_id = auth.user.id
    queue = InMemoryTaskQueue()  # o seed executa tudo aqui mesmo; nada vai para o worker

    resumes = ResumeService(session, user_id, settings, embeddings)
    text = await resumes.resolve_text(text=RESUME_TEXT, file=None)
    resume = (await resumes.create(title=RESUME_TITLE, text=text)).resume

    report = SeedReport(created=True)
    jobs = JobService(session, user_id, queue)
    analyses = AnalysisService(session, user_id, settings, queue)
    runner = AnalysisRunner(session, user_id, settings, llm, embeddings)
    first_analysis = None
    for data in JOBS:
        job = await jobs.create(data)
        await run_extraction_task(session, user_id, job.id, llm)
        request = AnalysisCreate(resume_id=resume.id, job_id=job.id)
        created = (await analyses.create(request)).analysis
        status = await runner.run(created.id)
        await session.refresh(created)
        report.analyses.append((job.title or "", status, created.score))
        if first_analysis is None and status == "done":
            first_analysis = created

    if first_analysis is not None:
        screening = ScreeningService(session, user_id, settings, llm, embeddings)
        answers = await screening.answer(
            first_analysis.id, ScreeningRequest(questions=SCREENING_QUESTIONS)
        )
        report.screening_needs_input = sum(a.needs_user_input for a in answers)
        await ApplicationService(session, user_id).create(
            ApplicationCreate(
                job_id=first_analysis.job_id,
                analysis_id=first_analysis.id,
                status="interview",
                platform="Site de vagas fictício",
                next_step="Entrevista técnica (exemplo)",
            )
        )
    return report


async def _main(reset: bool) -> int:
    settings = get_settings()
    if "fake" not in (settings.llm_provider, settings.embedding_provider):
        print(
            f"Atenção: provedores reais ({settings.llm_provider}/{settings.embedding_provider}); "
            "o seed vai gastar crédito de API.",
            file=sys.stderr,
        )
    engine = build_engine(settings.database_url, null_pool=True)
    llm = build_llm_provider(settings)
    embeddings = build_embedding_provider(settings)
    try:
        async with build_sessionmaker(engine)() as session:
            report = await seed(session, settings, llm, embeddings, reset=reset)
    except SeedRefusedError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    finally:
        await llm.aclose()
        await embeddings.aclose()
        await engine.dispose()

    if not report.created:
        print(f"A conta {DEMO_EMAIL} já existe. Use `make seed ARGS=--reset` para recriar.")
        return 0
    print(f"Conta de demonstração: {DEMO_EMAIL} / {DEMO_PASSWORD}")
    for title, status, score in report.analyses:
        print(f"  análise de '{title}': {status}, score {score}")
    print(f"  triagem: {report.screening_needs_input} resposta(s) precisam do seu input")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Cria dados fictícios de demonstração.")
    parser.add_argument("--reset", action="store_true", help="apaga e recria a conta demo")
    raise SystemExit(asyncio.run(_main(parser.parse_args().reset)))


if __name__ == "__main__":
    main()
