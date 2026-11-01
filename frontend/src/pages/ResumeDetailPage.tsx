import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { deleteResume, getResume } from "../api/resumes";
import { Alert } from "../components/ui/Alert";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { ConfirmDialog } from "../components/ui/ConfirmDialog";
import { ErrorState } from "../components/ui/ErrorState";
import { LinkButton } from "../components/ui/LinkButton";
import { PageHeader } from "../components/ui/PageHeader";
import { PageLoader } from "../components/ui/PageLoader";
import { getApiErrorMessage } from "../lib/errors";
import { formatChunkCount, formatDateTime } from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";

export function ResumeDetailPage() {
  const { resumeId } = useParams<{ resumeId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  const resumeQuery = useQuery({
    queryKey: ["resumes", resumeId ?? ""],
    queryFn: () => {
      if (!resumeId) throw new Error("Currículo não encontrado.");
      return getResume(resumeId);
    },
    enabled: Boolean(resumeId),
  });

  const resume = resumeQuery.data;

  usePageTitle(resume?.title ?? "Currículo");

  const deleteMutation = useMutation({
    mutationFn: deleteResume,
    onSuccess: () => {
      if (resumeId) queryClient.removeQueries({ queryKey: ["resumes", resumeId] });
      void queryClient.invalidateQueries({ queryKey: ["resumes"], exact: true });
      navigate("/curriculos", { replace: true });
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

  if (resumeQuery.isLoading) return <PageLoader label="Carregando currículo…" />;

  if (resumeQuery.isError || !resume) {
    return (
      <>
        <PageHeader backTo="/curriculos" backLabel="Currículos" title="Currículo" />
        <ErrorState
          description={
            resumeQuery.isError
              ? getApiErrorMessage(resumeQuery.error)
              : "Currículo não encontrado."
          }
          onRetry={resumeId ? () => void resumeQuery.refetch() : undefined}
        />
      </>
    );
  }

  return (
    <>
      <PageHeader
        backTo="/curriculos"
        backLabel="Currículos"
        title={resume.title}
        description={`Enviado em ${formatDateTime(resume.created_at)} · ${formatChunkCount(resume.chunks.length)}`}
        actions={
          <>
            <LinkButton to={`/analises/nova?curriculo=${resume.id}`}>Analisar com uma vaga</LinkButton>
            <Button variant="dangerGhost" onClick={openDeleteDialog}>
              Apagar
            </Button>
          </>
        }
      />

      <div className="flex flex-col gap-lg">
        <section aria-labelledby="chunks-title">
          <div className="mb-sm flex flex-wrap items-center justify-between gap-xs">
            <h2 id="chunks-title" className="text-lg font-semibold text-ink">
              Trechos do currículo
            </h2>
            <Badge tone="brand">{formatChunkCount(resume.chunks.length)}</Badge>
          </div>

          {resume.chunks.length === 0 ? (
            <Alert variant="warning">Este currículo não tem trechos para exibir.</Alert>
          ) : (
            <ol className="flex flex-col gap-sm">
              {resume.chunks.map((chunk) => (
                <li key={chunk.id}>
                  <Card className="p-lg">
                    <p className="mb-2xs text-xs font-medium uppercase tracking-wide text-muted">
                      Trecho {chunk.ordinal + 1}
                    </p>
                    <p className="whitespace-pre-wrap text-sm text-ink">{chunk.content}</p>
                  </Card>
                </li>
              ))}
            </ol>
          )}
        </section>

        <Card className="p-lg">
          <details>
            <summary className="cursor-pointer text-sm font-medium text-ink">
              Ver texto completo
            </summary>
            <p className="mt-sm whitespace-pre-wrap text-sm text-muted">{resume.raw_text}</p>
          </details>
        </Card>
      </div>

      <ConfirmDialog
        open={isDeleteOpen}
        title="Apagar currículo?"
        description={`"${resume.title}" e seus trechos serão apagados. Esta ação não pode ser desfeita.`}
        confirmLabel="Apagar currículo"
        tone="danger"
        isConfirming={deleteMutation.isPending}
        onClose={closeDeleteDialog}
        onConfirm={() => {
          if (resumeId) deleteMutation.mutate(resumeId);
        }}
      >
        {deleteMutation.isError ? (
          <Alert variant="error">{getApiErrorMessage(deleteMutation.error)}</Alert>
        ) : null}
      </ConfirmDialog>
    </>
  );
}
