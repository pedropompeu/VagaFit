import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { deleteJob, getJob } from "../api/jobs";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { ConfirmDialog } from "../components/ui/ConfirmDialog";
import { ErrorState } from "../components/ui/ErrorState";
import { LinkButton } from "../components/ui/LinkButton";
import { PageHeader } from "../components/ui/PageHeader";
import { PageLoader } from "../components/ui/PageLoader";
import { Spinner } from "../components/ui/Spinner";
import { getApiErrorMessage } from "../lib/errors";
import { formatDateTime, SENIORITY_LABELS, WORK_MODEL_LABELS } from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";
import type { JobRequirement } from "../types/api";

function RequirementList({ requirements }: { requirements: JobRequirement[] }) {
  return (
    <ul className="flex flex-col gap-xs">
      {requirements.map((requirement) => (
        <li key={requirement.id}>
          <Card className="flex items-start gap-sm p-md">
            <span className="mt-2xs shrink-0 text-xs font-semibold text-brand">
              {requirement.id}
            </span>
            <p className="text-sm text-ink">{requirement.text}</p>
          </Card>
        </li>
      ))}
    </ul>
  );
}

export function JobDetailPage() {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  const jobQuery = useQuery({
    queryKey: ["jobs", jobId ?? ""],
    queryFn: () => {
      if (!jobId) throw new Error("Vaga não encontrada.");
      return getJob(jobId);
    },
    enabled: Boolean(jobId),
    refetchInterval: (query) =>
      query.state.data?.extraction_status === "pending" ? 2000 : false,
  });

  const job = jobQuery.data;

  usePageTitle(job?.title ?? "Vaga");

  const deleteMutation = useMutation({
    mutationFn: deleteJob,
    onSuccess: () => {
      if (jobId) queryClient.removeQueries({ queryKey: ["jobs", jobId] });
      void queryClient.invalidateQueries({ queryKey: ["jobs"], exact: true });
      navigate("/vagas", { replace: true });
    },
  });

  function openDeleteDialog() {
    deleteMutation.reset();
    setIsDeleteOpen(true);
  }

  function closeDeleteDialog() {
    if (deleteMutation.isPending) return;
    setIsDeleteOpen(false);
    deleteMutation.reset();
  }

  if (jobQuery.isLoading) return <PageLoader label="Carregando vaga…" />;

  if (jobQuery.isError || !job) {
    return (
      <>
        <PageHeader backTo="/vagas" backLabel="Vagas" title="Vaga" />
        <ErrorState
          description={jobQuery.isError ? getApiErrorMessage(jobQuery.error) : "Vaga não encontrada."}
          onRetry={jobId ? () => void jobQuery.refetch() : undefined}
        />
      </>
    );
  }

  const extracted = job.extracted;
  const required = extracted?.requirements.filter((item) => item.kind === "required") ?? [];
  const niceToHave = extracted?.requirements.filter((item) => item.kind === "nice_to_have") ?? [];
  const company = job.company ?? extracted?.company ?? "Empresa não informada";
  const isPending = job.extraction_status === "pending";

  return (
    <>
      <PageHeader
        backTo="/vagas"
        backLabel="Vagas"
        title={job.title}
        description={`${company} · ${formatDateTime(job.created_at)}`}
        actions={
          <>
            <LinkButton to={`/analises/nova?vaga=${job.id}`}>Analisar com um currículo</LinkButton>
            <Button variant="dangerGhost" onClick={openDeleteDialog}>
              Apagar
            </Button>
          </>
        }
      />

      <div className="flex flex-col gap-lg">
        {isPending ? (
          <Alert variant="info" title="Extraindo requisitos">
            <div className="mt-2xs flex items-center gap-xs">
              <Spinner className="h-4 w-4" label="" />
              <span>A página atualiza sozinha assim que a extração terminar.</span>
            </div>
          </Alert>
        ) : null}

        {!isPending && !extracted ? (
          <Alert variant="warning">
            A extração terminou, mas nenhum requisito foi retornado para esta vaga.
          </Alert>
        ) : null}

        {extracted ? (
          <>
            <Card className="p-lg">
              <h2 className="text-base font-semibold text-ink">Resumo da vaga</h2>
              <dl className="mt-sm grid gap-md sm:grid-cols-3">
                <div>
                  <dt className="text-xs font-medium uppercase tracking-wide text-muted">
                    Senioridade
                  </dt>
                  <dd className="mt-2xs text-sm text-ink">
                    {SENIORITY_LABELS[extracted.seniority]}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-medium uppercase tracking-wide text-muted">
                    Modelo de trabalho
                  </dt>
                  <dd className="mt-2xs text-sm text-ink">
                    {WORK_MODEL_LABELS[extracted.work_model]}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs font-medium uppercase tracking-wide text-muted">
                    Localização
                  </dt>
                  <dd className="mt-2xs text-sm text-ink">
                    {extracted.location ?? "Não informada"}
                  </dd>
                </div>
              </dl>

              <div className="mt-md">
                <h3 className="text-sm font-medium text-ink">Stack</h3>
                {extracted.stack.length === 0 ? (
                  <p className="mt-xs text-sm text-muted">Nenhuma tecnologia identificada.</p>
                ) : (
                  <ul className="mt-xs flex flex-wrap gap-xs">
                    {extracted.stack.map((technology) => (
                      <li key={technology}>
                        <Badge tone="brand">{technology}</Badge>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </Card>

            <section aria-labelledby="required-title">
              <div className="mb-sm flex flex-wrap items-center gap-xs">
                <h2 id="required-title" className="text-lg font-semibold text-ink">
                  Requisitos obrigatórios
                </h2>
                <Badge tone="neutral">{required.length}</Badge>
              </div>
              {required.length === 0 ? (
                <p className="text-sm text-muted">Nenhum requisito obrigatório identificado.</p>
              ) : (
                <RequirementList requirements={required} />
              )}
            </section>

            <section aria-labelledby="nice-title">
              <div className="mb-sm flex flex-wrap items-center gap-xs">
                <h2 id="nice-title" className="text-lg font-semibold text-ink">
                  Diferenciais
                </h2>
                <Badge tone="neutral">{niceToHave.length}</Badge>
              </div>
              {niceToHave.length === 0 ? (
                <p className="text-sm text-muted">Nenhum diferencial identificado.</p>
              ) : (
                <RequirementList requirements={niceToHave} />
              )}
            </section>
          </>
        ) : null}

        <Card className="p-lg">
          <details>
            <summary className="cursor-pointer text-sm font-medium text-ink">
              Ver texto da vaga
            </summary>
            <p className="mt-sm whitespace-pre-wrap text-sm text-muted">{job.raw_text}</p>
          </details>
        </Card>
      </div>

      <ConfirmDialog
        open={isDeleteOpen}
        title="Apagar vaga?"
        description={`"${job.title}" e os requisitos extraídos serão apagados. Esta ação não pode ser desfeita.`}
        confirmLabel="Apagar vaga"
        tone="danger"
        isConfirming={deleteMutation.isPending}
        onClose={closeDeleteDialog}
        onConfirm={() => {
          if (jobId) deleteMutation.mutate(jobId);
        }}
      >
        {deleteMutation.isError ? (
          <Alert variant="error">{getApiErrorMessage(deleteMutation.error)}</Alert>
        ) : null}
      </ConfirmDialog>
    </>
  );
}
