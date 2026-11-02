import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";

import { listAnalyses } from "../api/analyses";
import { listJobs } from "../api/jobs";
import { listResumes } from "../api/resumes";
import { ScoreBadge } from "../components/analysis/ScoreBadge";
import { Badge } from "../components/ui/Badge";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { LinkButton } from "../components/ui/LinkButton";
import { PageHeader } from "../components/ui/PageHeader";
import { PageLoader } from "../components/ui/PageLoader";
import { getApiErrorMessage } from "../lib/errors";
import {
  ANALYSIS_STATUS_LABELS,
  ANALYSIS_STATUS_TONES,
  formatDateTime,
} from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";

export function AnalysesPage() {
  usePageTitle("Análises");

  const analysesQuery = useQuery({
    queryKey: ["analyses", "list"],
    queryFn: () => listAnalyses(),
    refetchInterval: (query) =>
      query.state.data?.some((item) => item.status === "pending" || item.status === "running")
        ? 3000
        : false,
  });
  const jobsQuery = useQuery({ queryKey: ["jobs"], queryFn: listJobs });
  const resumesQuery = useQuery({ queryKey: ["resumes"], queryFn: listResumes });

  const jobs = useMemo(
    () => new Map((jobsQuery.data ?? []).map((job) => [job.id, job])),
    [jobsQuery.data],
  );
  const resumes = useMemo(
    () => new Map((resumesQuery.data ?? []).map((resume) => [resume.id, resume])),
    [resumesQuery.data],
  );

  const analyses = analysesQuery.data ?? [];

  return (
    <>
      <PageHeader
        title="Análises"
        description="Cada análise compara um currículo com uma vaga e mostra a evidência de cada requisito."
        actions={<LinkButton to="/analises/nova">Nova análise</LinkButton>}
      />

      {analysesQuery.isLoading ? (
        <PageLoader label="Carregando análises…" />
      ) : analysesQuery.isError ? (
        <ErrorState
          description={getApiErrorMessage(analysesQuery.error)}
          onRetry={() => void analysesQuery.refetch()}
        />
      ) : analyses.length === 0 ? (
        <EmptyState
          title="Nenhuma análise ainda"
          description="Escolha um currículo e uma vaga. Cada requisito volta com o trecho do currículo que o comprova, ou como lacuna."
          action={<LinkButton to="/analises/nova">Criar primeira análise</LinkButton>}
        />
      ) : (
        <ul className="flex flex-col gap-sm">
          {analyses.map((analysis) => {
            const job = jobs.get(analysis.job_id);
            const resume = resumes.get(analysis.resume_id);
            return (
              <li key={analysis.id}>
                <Card className="flex flex-col gap-sm p-lg sm:flex-row sm:items-center sm:justify-between">
                  <div className="flex min-w-0 items-center gap-md">
                    <ScoreBadge score={analysis.score} className="shrink-0" />
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-xs">
                        <h2 className="truncate font-medium text-ink">
                          {job?.title ?? "Vaga removida"}
                        </h2>
                        <Badge tone={ANALYSIS_STATUS_TONES[analysis.status]}>
                          {ANALYSIS_STATUS_LABELS[analysis.status]}
                        </Badge>
                      </div>
                      <p className="mt-2xs text-sm text-muted">
                        {[job?.company, resume?.title, formatDateTime(analysis.created_at)]
                          .filter(Boolean)
                          .join(" · ")}
                      </p>
                    </div>
                  </div>
                  <LinkButton to={`/analises/${analysis.id}`} variant="secondary" size="sm">
                    Abrir
                  </LinkButton>
                </Card>
              </li>
            );
          })}
        </ul>
      )}
    </>
  );
}
