import { TrashIcon } from "@heroicons/react/24/outline";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { deleteJob, listJobs } from "../api/jobs";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { ConfirmDialog } from "../components/ui/ConfirmDialog";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { LinkButton } from "../components/ui/LinkButton";
import { PageHeader } from "../components/ui/PageHeader";
import { PageLoader } from "../components/ui/PageLoader";
import { Spinner } from "../components/ui/Spinner";
import { getApiErrorMessage } from "../lib/errors";
import { formatDateTime } from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";
import type { JobSummary } from "../types/api";

export function JobsPage() {
  usePageTitle("Vagas");

  const queryClient = useQueryClient();
  const [jobToDelete, setJobToDelete] = useState<JobSummary | null>(null);

  const jobsQuery = useQuery({
    queryKey: ["jobs"],
    queryFn: listJobs,
    refetchInterval: (query) =>
      query.state.data?.some((job) => job.extraction_status === "pending") ? 3000 : false,
  });

  const deleteMutation = useMutation({
    mutationFn: deleteJob,
    onSuccess: (_data, id) => {
      setJobToDelete(null);
      queryClient.removeQueries({ queryKey: ["jobs", id] });
      void queryClient.invalidateQueries({ queryKey: ["jobs"], exact: true });
    },
  });

  function openDeleteDialog(job: JobSummary) {
    deleteMutation.reset();
    setJobToDelete(job);
  }

  function closeDeleteDialog() {
    if (deleteMutation.isPending) return;
    setJobToDelete(null);
    deleteMutation.reset();
  }

  const jobs = jobsQuery.data ?? [];
  const pendingCount = jobs.filter((job) => job.extraction_status === "pending").length;
  const isInitialLoading = jobsQuery.isLoading || (jobsQuery.isFetching && jobs.length === 0);

  return (
    <>
      <PageHeader
        title="Vagas"
        description="Cole o texto das vagas. O VagaFit extrai os requisitos para as análises."
        actions={<LinkButton to="/vagas/nova">Colar vaga</LinkButton>}
      />

      {pendingCount > 0 ? (
        <div className="mb-md">
          <Alert variant="info">
            <div className="flex items-center gap-xs">
              <Spinner className="h-4 w-4" label="" />
              <span>
                Extraindo requisitos de {pendingCount === 1 ? "1 vaga" : `${pendingCount} vagas`}. A
                lista atualiza sozinha.
              </span>
            </div>
          </Alert>
        </div>
      ) : null}

      {isInitialLoading ? (
        <PageLoader label="Carregando vagas…" />
      ) : jobsQuery.isError ? (
        <ErrorState
          description={getApiErrorMessage(jobsQuery.error)}
          onRetry={() => void jobsQuery.refetch()}
        />
      ) : jobs.length === 0 ? (
        <EmptyState
          title="Nenhuma vaga ainda"
          description="Cole o texto de uma vaga. O VagaFit extrai os requisitos e você confere a lista antes de analisar."
          action={<LinkButton to="/vagas/nova">Colar vaga</LinkButton>}
        />
      ) : (
        <ul className="flex flex-col gap-sm">
          {jobs.map((job) => {
            const isPending = job.extraction_status === "pending";
            return (
              <li key={job.id}>
                <Card className="flex flex-col gap-sm p-lg sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-xs">
                      <h2 className="truncate font-medium text-ink">{job.title}</h2>
                      <Badge tone={isPending ? "warning" : "success"}>
                        {isPending ? "Extraindo requisitos…" : "Requisitos extraídos"}
                      </Badge>
                    </div>
                    <p className="mt-2xs text-sm text-muted">
                      {job.company ?? "Empresa não informada"} · {formatDateTime(job.created_at)}
                    </p>
                  </div>
                  <div className="flex shrink-0 items-center gap-xs">
                    <LinkButton to={`/vagas/${job.id}`} variant="secondary" size="sm">
                      Abrir
                    </LinkButton>
                    <Button variant="dangerGhost" size="sm" onClick={() => openDeleteDialog(job)}>
                      <TrashIcon className="size-4" aria-hidden="true" />
                      Apagar
                    </Button>
                  </div>
                </Card>
              </li>
            );
          })}
        </ul>
      )}

      <ConfirmDialog
        open={jobToDelete !== null}
        title="Apagar vaga?"
        description={
          jobToDelete
            ? `"${jobToDelete.title}" e os requisitos extraídos serão apagados. Esta ação não pode ser desfeita.`
            : undefined
        }
        confirmLabel="Apagar vaga"
        tone="danger"
        isConfirming={deleteMutation.isPending}
        onClose={closeDeleteDialog}
        onConfirm={() => {
          if (jobToDelete) deleteMutation.mutate(jobToDelete.id);
        }}
      >
        {deleteMutation.isError ? (
          <Alert variant="error">{getApiErrorMessage(deleteMutation.error)}</Alert>
        ) : null}
      </ConfirmDialog>
    </>
  );
}
