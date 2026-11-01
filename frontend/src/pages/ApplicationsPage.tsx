import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useSearchParams } from "react-router-dom";

import { deleteApplication, listApplications, updateApplication } from "../api/applications";
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
import { Select } from "../components/ui/Select";
import { cn } from "../lib/cn";
import { getApiErrorMessage } from "../lib/errors";
import {
  APPLICATION_STATUS_LABELS,
  APPLICATION_STATUS_TONES,
  formatCurrency,
  formatPlainDate,
} from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";
import { APPLICATION_STATUSES, type Application, type ApplicationStatus } from "../types/api";

function isStatus(value: string): value is ApplicationStatus {
  return (APPLICATION_STATUSES as readonly string[]).includes(value);
}

export function ApplicationsPage() {
  usePageTitle("Candidaturas");

  const queryClient = useQueryClient();
  const [searchParams, setSearchParams] = useSearchParams();
  const selected = searchParams.getAll("status").filter(isStatus);
  const [toDelete, setToDelete] = useState<Application | null>(null);

  const applicationsQuery = useQuery({
    queryKey: ["applications", "list", selected],
    queryFn: () => listApplications(selected),
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: ApplicationStatus }) =>
      updateApplication(id, { status }),
    onSuccess: () => void queryClient.invalidateQueries({ queryKey: ["applications"] }),
  });

  const deleteMutation = useMutation({
    mutationFn: deleteApplication,
    onSuccess: () => {
      setToDelete(null);
      void queryClient.invalidateQueries({ queryKey: ["applications"] });
    },
  });

  function toggleStatus(status: ApplicationStatus) {
    const next = selected.includes(status)
      ? selected.filter((item) => item !== status)
      : [...selected, status];
    const params = new URLSearchParams();
    for (const item of APPLICATION_STATUSES) if (next.includes(item)) params.append("status", item);
    setSearchParams(params, { replace: true });
  }

  function closeDeleteDialog() {
    if (deleteMutation.isPending) return;
    setToDelete(null);
    deleteMutation.reset();
  }

  const applications = applicationsQuery.data ?? [];

  return (
    <>
      <PageHeader
        title="Candidaturas"
        description="Acompanhe onde você se candidatou, em que etapa está e qual é o próximo passo."
        actions={<LinkButton to="/candidaturas/nova">Nova candidatura</LinkButton>}
      />

      <div className="mb-md flex flex-wrap items-center gap-xs" role="group" aria-label="Filtrar por status">
        {APPLICATION_STATUSES.map((status) => {
          const active = selected.includes(status);
          return (
            <button
              key={status}
              type="button"
              aria-pressed={active}
              onClick={() => toggleStatus(status)}
              className={cn(
                "rounded-full border px-sm py-2xs text-sm font-medium transition-colors",
                active ? "border-brand bg-brand-soft text-brand" : "border-line text-muted hover:text-brand",
              )}
            >
              {APPLICATION_STATUS_LABELS[status]}
            </button>
          );
        })}
        {selected.length > 0 ? (
          <Button variant="ghost" size="sm" onClick={() => setSearchParams({}, { replace: true })}>
            Limpar filtros
          </Button>
        ) : null}
      </div>

      {statusMutation.isError ? (
        <div className="mb-md">
          <Alert variant="error">{getApiErrorMessage(statusMutation.error)}</Alert>
        </div>
      ) : null}

      {applicationsQuery.isLoading ? (
        <PageLoader label="Carregando candidaturas…" />
      ) : applicationsQuery.isError ? (
        <ErrorState
          description={getApiErrorMessage(applicationsQuery.error)}
          onRetry={() => void applicationsQuery.refetch()}
        />
      ) : applications.length === 0 ? (
        selected.length > 0 ? (
          <EmptyState
            title="Nenhuma candidatura com esses status"
            description="Tire algum filtro para ver as outras."
          />
        ) : (
          <EmptyState
            title="Nenhuma candidatura registrada"
            description="Registre as vagas em que você se candidatou para acompanhar cada etapa."
            action={<LinkButton to="/candidaturas/nova">Registrar candidatura</LinkButton>}
          />
        )
      ) : (
        <ul className="flex flex-col gap-sm">
          {applications.map((application) => {
            const details = [
              application.job.company ?? "Empresa não informada",
              application.platform,
              `Desde ${formatPlainDate(application.applied_at)}`,
              application.salary_expectation !== null
                ? `Pretensão ${formatCurrency(application.salary_expectation)}`
                : null,
            ].filter(Boolean);
            const selectId = `status-${application.id}`;
            return (
              <li key={application.id}>
                <Card className="flex flex-col gap-sm p-lg md:flex-row md:items-center md:justify-between">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-xs">
                      <h2 className="truncate font-medium text-ink">{application.job.title}</h2>
                      <Badge tone={APPLICATION_STATUS_TONES[application.status]}>
                        {APPLICATION_STATUS_LABELS[application.status]}
                      </Badge>
                    </div>
                    <p className="mt-2xs text-sm text-muted">{details.join(" · ")}</p>
                    {application.next_step ? (
                      <p className="mt-2xs text-sm text-ink">
                        <span className="font-medium">Próximo passo:</span> {application.next_step}
                      </p>
                    ) : null}
                  </div>
                  <div className="flex shrink-0 flex-wrap items-center gap-xs">
                    <label htmlFor={selectId} className="sr-only">
                      Status de {application.job.title}
                    </label>
                    <Select
                      id={selectId}
                      className="w-auto"
                      value={application.status}
                      disabled={
                        statusMutation.isPending && statusMutation.variables?.id === application.id
                      }
                      onChange={(event) => {
                        if (isStatus(event.target.value)) {
                          statusMutation.mutate({ id: application.id, status: event.target.value });
                        }
                      }}
                    >
                      {APPLICATION_STATUSES.map((status) => (
                        <option key={status} value={status}>
                          {APPLICATION_STATUS_LABELS[status]}
                        </option>
                      ))}
                    </Select>
                    {application.analysis_id ? (
                      <LinkButton to={`/analises/${application.analysis_id}`} variant="ghost" size="sm">
                        Análise
                      </LinkButton>
                    ) : null}
                    <LinkButton
                      to={`/candidaturas/${application.id}/editar`}
                      variant="secondary"
                      size="sm"
                    >
                      Editar
                    </LinkButton>
                    <Button
                      variant="dangerGhost"
                      size="sm"
                      onClick={() => {
                        deleteMutation.reset();
                        setToDelete(application);
                      }}
                    >
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
        open={toDelete !== null}
        title="Apagar candidatura?"
        description={
          toDelete
            ? `A candidatura para "${toDelete.job.title}" será apagada. A vaga e a análise continuam.`
            : undefined
        }
        confirmLabel="Apagar candidatura"
        tone="danger"
        isConfirming={deleteMutation.isPending}
        onClose={closeDeleteDialog}
        onConfirm={() => {
          if (toDelete) deleteMutation.mutate(toDelete.id);
        }}
      >
        {deleteMutation.isError ? (
          <Alert variant="error">{getApiErrorMessage(deleteMutation.error)}</Alert>
        ) : null}
      </ConfirmDialog>
    </>
  );
}
