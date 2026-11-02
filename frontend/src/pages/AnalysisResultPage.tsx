import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { createAnalysis, getAnalysis } from "../api/analyses";
import { getJob } from "../api/jobs";
import { getResume } from "../api/resumes";
import { EvidenceList } from "../components/analysis/EvidenceList";
import { ScoreBadge } from "../components/analysis/ScoreBadge";
import { ScreeningSection } from "../components/analysis/ScreeningSection";
import { VerdictBadge } from "../components/analysis/VerdictBadge";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Disclosure } from "../components/ui/Disclosure";
import { ErrorState } from "../components/ui/ErrorState";
import { LinkButton } from "../components/ui/LinkButton";
import { PageHeader } from "../components/ui/PageHeader";
import { PageLoader } from "../components/ui/PageLoader";
import { Spinner } from "../components/ui/Spinner";
import { getApiErrorMessage } from "../lib/errors";
import {
  ANALYSIS_STATUS_LABELS,
  countWithEvidence,
  formatDateTime,
  formatEvidenceCount,
  KIND_LABELS,
  SENIORITY_LABELS,
  WORK_MODEL_LABELS,
} from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";
import type { AnalysisResult, RequirementResult, ResumeChunk } from "../types/api";

function ScoreCard({ result }: { result: AnalysisResult }) {
  // O percentual ponderado só define o comprimento; o texto é a contagem (BRAND.md 10).
  const breakdown = [
    ["Obrigatórios", result.breakdown.required, countWithEvidence(result.requirements, "required")],
    ["Diferenciais", result.breakdown.nice_to_have, countWithEvidence(result.requirements, "nice_to_have")],
  ] as const;

  return (
    <Card className="flex flex-col gap-md p-lg sm:flex-row sm:items-center sm:gap-xl">
      <div className="flex flex-col gap-xs sm:max-w-[16rem]">
        <ScoreBadge score={result.score} size="lg" showLabel />
        <p className="text-caption text-muted">
          Resume o quanto o currículo comprova os requisitos desta vaga. Obrigatórios pesam mais. Não avalia você.
        </p>
      </div>
      <dl className="grid flex-1 gap-sm sm:grid-cols-2">
        {breakdown.map(([label, value, count]) => (
          <div key={label}>
            <dt className="text-sm text-muted">{label}</dt>
            <dd className="mt-2xs">
              {value === null ? (
                <div className="flex items-center gap-xs">
                  <div
                    className="h-2 flex-1 rounded-full border border-dashed border-line-strong"
                    aria-hidden="true"
                  />
                  <span className="text-sm text-muted">A vaga não lista.</span>
                </div>
              ) : (
                <div className="flex items-center gap-xs">
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-dataviz-track" aria-hidden="true">
                    <div className="h-full rounded-full bg-dataviz-1" style={{ width: `${value * 100}%` }} />
                  </div>
                  <span className="whitespace-nowrap text-right font-mono text-mono-sm tabular-nums text-ink">
                    {formatEvidenceCount(count.withEvidence, count.total)}
                  </span>
                </div>
              )}
            </dd>
          </div>
        ))}
      </dl>
    </Card>
  );
}

function RequirementRow({
  requirement,
  chunks,
}: {
  requirement: RequirementResult;
  chunks: Map<string, ResumeChunk>;
}) {
  return (
    <li>
      <Card className="p-md">
        <div className="flex flex-wrap items-start justify-between gap-sm">
          <div className="min-w-0 flex-1">
            <p className="text-sm font-medium text-ink">{requirement.text}</p>
            <p className="mt-2xs text-xs text-muted">{KIND_LABELS[requirement.kind]}</p>
          </div>
          <VerdictBadge verdict={requirement.verdict} hasEvidence={requirement.evidence.length > 0} />
        </div>
        {requirement.rationale ? (
          <p className="mt-xs text-sm text-muted">{requirement.rationale}</p>
        ) : null}
        {requirement.evidence.length > 0 ? (
          <Disclosure summary={<>Evidência no currículo ({requirement.evidence.length})</>} className="mt-xs">
            <div className="mt-xs">
              <EvidenceList evidence={requirement.evidence} chunks={chunks} />
            </div>
          </Disclosure>
        ) : (
          <p className="mt-xs text-xs text-muted">Nenhum trecho do currículo comprova este item.</p>
        )}
      </Card>
    </li>
  );
}

function ResultSections({
  result,
  chunks,
}: {
  result: AnalysisResult;
  chunks: Map<string, ResumeChunk>;
}) {
  return (
    <>
      <ScoreCard result={result} />

      <Card className="p-lg">
        <dl className="grid gap-md sm:grid-cols-3">
          <div>
            <dt className="text-caption text-muted">Senioridade</dt>
            <dd className="mt-2xs text-sm text-ink">{SENIORITY_LABELS[result.job.seniority]}</dd>
          </div>
          <div>
            <dt className="text-caption text-muted">Modelo</dt>
            <dd className="mt-2xs text-sm text-ink">{WORK_MODEL_LABELS[result.job.work_model]}</dd>
          </div>
          <div>
            <dt className="text-caption text-muted">Stack</dt>
            <dd className="mt-2xs flex flex-wrap gap-2xs">
              {result.job.stack.length === 0 ? (
                <span className="text-sm text-muted">Não identificada</span>
              ) : (
                result.job.stack.map((tech) => (
                  <Badge key={tech} tone="brand">
                    {tech}
                  </Badge>
                ))
              )}
            </dd>
          </div>
        </dl>
      </Card>

      <section aria-labelledby="requirements-title">
        <h2 id="requirements-title" className="mb-sm text-lg font-semibold text-ink">
          Requisitos
        </h2>
        {result.requirements.length === 0 ? (
          <p className="text-sm text-muted">A vaga não tem requisitos extraídos.</p>
        ) : (
          <ul className="flex flex-col gap-xs">
            {result.requirements.map((requirement) => (
              <RequirementRow key={requirement.id} requirement={requirement} chunks={chunks} />
            ))}
          </ul>
        )}
      </section>

      <section aria-labelledby="gaps-title">
        <h2 id="gaps-title" className="mb-sm text-lg font-semibold text-ink">
          Lacunas
        </h2>
        {result.gaps.length === 0 ? (
          <p className="text-sm text-muted">Nenhuma lacuna: o currículo cobre todos os requisitos.</p>
        ) : (
          <Card className="p-md">
            <ul className="flex flex-col gap-xs">
              {result.gaps.map((gap) => (
                <li key={gap.requirement_id} className="flex flex-wrap items-center gap-xs text-sm">
                  <VerdictBadge verdict={gap.verdict} hasEvidence={false} />
                  <span className="text-ink">{gap.text}</span>
                  <span className="text-xs text-muted">· {KIND_LABELS[gap.kind]}</span>
                </li>
              ))}
            </ul>
          </Card>
        )}
      </section>

      <section aria-labelledby="suggestions-title">
        <h2 id="suggestions-title" className="mb-2xs text-lg font-semibold text-ink">
          Sugestões de reescrita
        </h2>
        <p className="mb-sm text-sm text-muted">
          Só reformulam o que já está no currículo. Nenhum fato novo entra.
        </p>
        {result.suggestions.length === 0 ? (
          <p className="text-sm text-muted">Nenhuma sugestão para este par.</p>
        ) : (
          <ul className="flex flex-col gap-xs">
            {result.suggestions.map((item, index) => (
              <li key={`${item.chunk_id}-${index}`}>
                <Card className="grid gap-sm p-md sm:grid-cols-[1fr_auto_1fr] sm:items-start">
                  <p className="text-sm text-muted line-through decoration-line">{item.original}</p>
                  <span aria-hidden="true" className="text-center text-brand">
                    →
                  </span>
                  <p className="text-sm text-ink">
                    <span className="sr-only">Sugestão: </span>
                    {item.suggestion}
                  </p>
                </Card>
              </li>
            ))}
          </ul>
        )}
      </section>

      <p className="text-xs text-muted">
        Modelo {result.model} · prompt {result.prompt_version}
      </p>
    </>
  );
}

export function AnalysisResultPage() {
  const { analysisId } = useParams<{ analysisId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const analysisQuery = useQuery({
    queryKey: ["analyses", "detail", analysisId ?? ""],
    queryFn: () => {
      if (!analysisId) throw new Error("Análise não encontrada.");
      return getAnalysis(analysisId);
    },
    enabled: Boolean(analysisId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "pending" || status === "running" ? 2000 : false;
    },
  });
  const analysis = analysisQuery.data;

  const jobQuery = useQuery({
    queryKey: ["jobs", analysis?.job_id ?? ""],
    queryFn: () => getJob(analysis!.job_id),
    enabled: Boolean(analysis?.job_id),
  });
  const resumeQuery = useQuery({
    queryKey: ["resumes", analysis?.resume_id ?? ""],
    queryFn: () => getResume(analysis!.resume_id),
    enabled: analysis?.status === "done",
  });

  const chunks = useMemo(
    () => new Map((resumeQuery.data?.chunks ?? []).map((chunk) => [chunk.id, chunk])),
    [resumeQuery.data],
  );

  const jobTitle = analysis?.result?.job.title ?? jobQuery.data?.title ?? "Análise";
  usePageTitle(`Análise: ${jobTitle}`);

  const retryMutation = useMutation({
    mutationFn: () => createAnalysis({ resume_id: analysis!.resume_id, job_id: analysis!.job_id }),
    onSuccess: (created) => {
      void queryClient.invalidateQueries({ queryKey: ["analyses"] });
      navigate(`/analises/${created.id}`, { replace: true });
    },
  });

  if (analysisQuery.isLoading) return <PageLoader label="Carregando análise…" />;

  if (analysisQuery.isError || !analysis) {
    return (
      <>
        <PageHeader backTo="/analises" backLabel="Análises" title="Análise" />
        <ErrorState
          description={
            analysisQuery.isError ? getApiErrorMessage(analysisQuery.error) : "Análise não encontrada."
          }
          onRetry={analysisId ? () => void analysisQuery.refetch() : undefined}
        />
      </>
    );
  }

  const company = jobQuery.data?.company;
  const resumeTitle = resumeQuery.data?.title;
  const description = [company, resumeTitle && `Currículo: ${resumeTitle}`, formatDateTime(analysis.created_at)]
    .filter(Boolean)
    .join(" · ");
  const isRunning = analysis.status === "pending" || analysis.status === "running";

  return (
    <>
      <PageHeader
        backTo="/analises"
        backLabel="Análises"
        title={jobTitle}
        description={description}
        actions={
          analysis.status === "done" ? (
            <LinkButton
              to={`/candidaturas/nova?vaga=${analysis.job_id}&analise=${analysis.id}`}
            >
              Registrar candidatura
            </LinkButton>
          ) : undefined
        }
      />

      <div className="flex flex-col gap-lg">
        {isRunning ? (
          <Alert variant="info" title={ANALYSIS_STATUS_LABELS[analysis.status]}>
            <div className="mt-2xs flex items-center gap-xs">
              <Spinner className="h-4 w-4" label="" />
              <span>Comparando o currículo com cada requisito. A página atualiza sozinha.</span>
            </div>
          </Alert>
        ) : null}

        {analysis.status === "failed" ? (
          <Alert variant="error" title="A análise falhou">
            <p>{analysis.error ?? "Não foi possível concluir a análise."}</p>
            <div className="mt-sm">
              <Button
                variant="secondary"
                size="sm"
                isLoading={retryMutation.isPending}
                onClick={() => retryMutation.mutate()}
              >
                Tentar de novo
              </Button>
            </div>
            {retryMutation.isError ? (
              <p className="mt-xs">{getApiErrorMessage(retryMutation.error)}</p>
            ) : null}
          </Alert>
        ) : null}

        {analysis.status === "done" && analysis.result ? (
          <>
            {resumeQuery.isError ? (
              <Alert variant="warning">
                Não deu para carregar o currículo; as citações aparecem sem o trecho completo.
              </Alert>
            ) : null}
            <ResultSections result={analysis.result} chunks={chunks} />
            <ScreeningSection analysisId={analysis.id} chunks={chunks} />
          </>
        ) : null}
      </div>
    </>
  );
}
