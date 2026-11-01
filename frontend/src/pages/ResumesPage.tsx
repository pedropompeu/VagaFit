import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { deleteResume, listResumes } from "../api/resumes";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { ConfirmDialog } from "../components/ui/ConfirmDialog";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { LinkButton } from "../components/ui/LinkButton";
import { PageHeader } from "../components/ui/PageHeader";
import { PageLoader } from "../components/ui/PageLoader";
import { getApiErrorMessage } from "../lib/errors";
import { formatChunkCount, formatDateTime } from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";
import type { ResumeSummary } from "../types/api";

export function ResumesPage() {
  usePageTitle("Currículos");

  const queryClient = useQueryClient();
  const [resumeToDelete, setResumeToDelete] = useState<ResumeSummary | null>(null);

  const resumesQuery = useQuery({ queryKey: ["resumes"], queryFn: listResumes });

  const deleteMutation = useMutation({
    mutationFn: deleteResume,
    onSuccess: (_data, id) => {
      setResumeToDelete(null);
      queryClient.removeQueries({ queryKey: ["resumes", id] });
      void queryClient.invalidateQueries({ queryKey: ["resumes"], exact: true });
    },
  });

  function openDeleteDialog(resume: ResumeSummary) {
    deleteMutation.reset();
    setResumeToDelete(resume);
  }

  function closeDeleteDialog() {
    if (deleteMutation.isPending) return;
    setResumeToDelete(null);
    deleteMutation.reset();
  }

  const resumes = resumesQuery.data ?? [];
  const isInitialLoading = resumesQuery.isLoading || (resumesQuery.isFetching && resumes.length === 0);

  return (
    <>
      <PageHeader
        title="Currículos"
        description="Cadastre versões do seu currículo para usar nas análises de aderência."
        actions={<LinkButton to="/curriculos/novo">Novo currículo</LinkButton>}
      />

      {isInitialLoading ? (
        <PageLoader label="Carregando currículos…" />
      ) : resumesQuery.isError ? (
        <ErrorState
          description={getApiErrorMessage(resumesQuery.error)}
          onRetry={() => void resumesQuery.refetch()}
        />
      ) : resumes.length === 0 ? (
        <EmptyState
          title="Nenhum currículo cadastrado"
          description="Cole o texto do seu currículo ou envie um PDF para começar."
          action={<LinkButton to="/curriculos/novo">Cadastrar currículo</LinkButton>}
        />
      ) : (
        <ul className="flex flex-col gap-sm">
          {resumes.map((resume) => (
            <li key={resume.id}>
              <Card className="flex flex-col gap-sm p-lg sm:flex-row sm:items-center sm:justify-between">
                <div className="min-w-0">
                  <h2 className="truncate font-medium text-ink">{resume.title}</h2>
                  <p className="mt-2xs text-sm text-muted">
                    {formatDateTime(resume.created_at)} · {formatChunkCount(resume.chunk_count)}
                  </p>
                </div>
                <div className="flex shrink-0 items-center gap-xs">
                  <LinkButton to={`/curriculos/${resume.id}`} variant="secondary" size="sm">
                    Abrir
                  </LinkButton>
                  <Button
                    variant="dangerGhost"
                    size="sm"
                    onClick={() => openDeleteDialog(resume)}
                  >
                    Apagar
                  </Button>
                </div>
              </Card>
            </li>
          ))}
        </ul>
      )}

      <ConfirmDialog
        open={resumeToDelete !== null}
        title="Apagar currículo?"
        description={
          resumeToDelete
            ? `"${resumeToDelete.title}" e seus trechos serão apagados. Esta ação não pode ser desfeita.`
            : undefined
        }
        confirmLabel="Apagar currículo"
        tone="danger"
        isConfirming={deleteMutation.isPending}
        onClose={closeDeleteDialog}
        onConfirm={() => {
          if (resumeToDelete) deleteMutation.mutate(resumeToDelete.id);
        }}
      >
        {deleteMutation.isError ? (
          <Alert variant="error">{getApiErrorMessage(deleteMutation.error)}</Alert>
        ) : null}
      </ConfirmDialog>
    </>
  );
}
