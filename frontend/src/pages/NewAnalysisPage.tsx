import { DocumentMagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

import { createAnalysis } from "../api/analyses";
import { createJob, listJobs } from "../api/jobs";
import { listResumes } from "../api/resumes";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { EmptyState } from "../components/ui/EmptyState";
import { ErrorState } from "../components/ui/ErrorState";
import { Field } from "../components/ui/Field";
import { Input } from "../components/ui/Input";
import { LinkButton } from "../components/ui/LinkButton";
import { PageHeader } from "../components/ui/PageHeader";
import { PageLoader } from "../components/ui/PageLoader";
import { Select } from "../components/ui/Select";
import { Textarea } from "../components/ui/Textarea";
import { cn } from "../lib/cn";
import { getApiErrorMessage } from "../lib/errors";
import { usePageTitle } from "../lib/usePageTitle";

const MIN_JOB_TEXT = 20;
const MAX_JOB_TEXT = 30_000;

type JobMode = "existing" | "new";

export function NewAnalysisPage() {
  usePageTitle("Nova análise");

  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();

  const resumesQuery = useQuery({ queryKey: ["resumes"], queryFn: listResumes });
  const jobsQuery = useQuery({ queryKey: ["jobs"], queryFn: listJobs });

  const [resumeId, setResumeId] = useState(searchParams.get("curriculo") ?? "");
  const [jobId, setJobId] = useState(searchParams.get("vaga") ?? "");
  const [jobMode, setJobMode] = useState<JobMode>("existing");
  const [jobTitle, setJobTitle] = useState("");
  const [jobCompany, setJobCompany] = useState("");
  const [jobText, setJobText] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const resumes = resumesQuery.data ?? [];
  const jobs = jobsQuery.data ?? [];
  // Sem escolha explícita, usa o único item disponível ou o primeiro da lista.
  const selectedResumeId = resumeId || resumes[0]?.id || "";
  const selectedJobId = jobId || jobs[0]?.id || "";
  const effectiveJobMode: JobMode = jobs.length === 0 ? "new" : jobMode;

  const submitMutation = useMutation({
    mutationFn: async () => {
      let targetJobId = selectedJobId;
      if (effectiveJobMode === "new") {
        const job = await createJob({
          raw_text: jobText.trim(),
          title: jobTitle.trim() || undefined,
          company: jobCompany.trim() || undefined,
        });
        void queryClient.invalidateQueries({ queryKey: ["jobs"], exact: true });
        targetJobId = job.id;
      }
      return createAnalysis({ resume_id: selectedResumeId, job_id: targetJobId });
    },
    onSuccess: (analysis) => {
      void queryClient.invalidateQueries({ queryKey: ["analyses"] });
      navigate(`/analises/${analysis.id}`);
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);
    if (!selectedResumeId) {
      setFormError("Escolha um currículo.");
      return;
    }
    if (effectiveJobMode === "existing" && !selectedJobId) {
      setFormError("Escolha uma vaga.");
      return;
    }
    if (effectiveJobMode === "new" && jobText.trim().length < MIN_JOB_TEXT) {
      setFormError("Cole o texto da vaga com pelo menos 20 caracteres.");
      return;
    }
    submitMutation.mutate();
  }

  const header = (
    <PageHeader
      backTo="/analises"
      backLabel="Análises"
      title="Nova análise"
      description="Compare um currículo com uma vaga. Cada requisito volta com a evidência tirada do currículo."
    />
  );

  if (resumesQuery.isLoading || jobsQuery.isLoading) {
    return (
      <>
        {header}
        <PageLoader label="Carregando currículos e vagas…" />
      </>
    );
  }

  if (resumesQuery.isError || jobsQuery.isError) {
    return (
      <>
        {header}
        <ErrorState
          description={getApiErrorMessage(resumesQuery.error ?? jobsQuery.error)}
          onRetry={() => {
            void resumesQuery.refetch();
            void jobsQuery.refetch();
          }}
        />
      </>
    );
  }

  if (resumes.length === 0) {
    return (
      <>
        {header}
        <EmptyState
          title="Adicione um currículo primeiro"
          description="A análise compara um currículo seu com os requisitos da vaga."
          action={<LinkButton to="/curriculos/novo">Adicionar currículo</LinkButton>}
        />
      </>
    );
  }

  const error =
    formError ?? (submitMutation.isError ? getApiErrorMessage(submitMutation.error) : null);

  return (
    <>
      {header}

      <form onSubmit={handleSubmit} className="flex flex-col gap-lg">
        {error ? <Alert variant="error">{error}</Alert> : null}

        <Card className="flex flex-col gap-md p-lg">
          <Field label="Currículo" htmlFor="analysis-resume" required>
            <Select
              id="analysis-resume"
              value={selectedResumeId}
              onChange={(event) => setResumeId(event.target.value)}
            >
              {resumes.map((resume) => (
                <option key={resume.id} value={resume.id}>
                  {resume.title}
                </option>
              ))}
            </Select>
          </Field>

          <fieldset className="flex flex-col gap-sm">
            <legend className="text-sm font-medium text-ink">Vaga</legend>
            {jobs.length > 0 ? (
              <div className="flex flex-wrap gap-xs" role="radiogroup" aria-label="Origem da vaga">
                {(
                  [
                    ["existing", "Vaga salva"],
                    ["new", "Colar vaga nova"],
                  ] as const
                ).map(([mode, label]) => (
                  <button
                    key={mode}
                    type="button"
                    role="radio"
                    aria-checked={effectiveJobMode === mode}
                    onClick={() => setJobMode(mode)}
                    className={cn(
                      "rounded-full border px-sm py-2xs text-sm font-medium transition-colors",
                      effectiveJobMode === mode
                        ? "border-brand bg-brand-soft text-brand"
                        : "border-line text-muted hover:text-brand",
                    )}
                  >
                    {label}
                  </button>
                ))}
              </div>
            ) : null}

            {effectiveJobMode === "existing" ? (
              <Field label="Vaga salva" htmlFor="analysis-job" required>
                <Select
                  id="analysis-job"
                  value={selectedJobId}
                  onChange={(event) => setJobId(event.target.value)}
                >
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.company ? `${job.title} · ${job.company}` : job.title}
                    </option>
                  ))}
                </Select>
              </Field>
            ) : (
              <>
                <div className="grid gap-md sm:grid-cols-2">
                  <Field label="Cargo" htmlFor="analysis-job-title" hint="Opcional.">
                    <Input
                      id="analysis-job-title"
                      maxLength={160}
                      value={jobTitle}
                      onChange={(event) => setJobTitle(event.target.value)}
                    />
                  </Field>
                  <Field label="Empresa" htmlFor="analysis-job-company" hint="Opcional.">
                    <Input
                      id="analysis-job-company"
                      maxLength={160}
                      value={jobCompany}
                      onChange={(event) => setJobCompany(event.target.value)}
                    />
                  </Field>
                </div>
                <Field
                  label="Texto da vaga"
                  htmlFor="analysis-job-text"
                  required
                  hint={`${jobText.length.toLocaleString("pt-BR")} de ${MAX_JOB_TEXT.toLocaleString("pt-BR")} caracteres · mínimo de ${MIN_JOB_TEXT}`}
                >
                  <Textarea
                    id="analysis-job-text"
                    rows={10}
                    maxLength={MAX_JOB_TEXT}
                    aria-describedby="analysis-job-text-hint"
                    value={jobText}
                    onChange={(event) => setJobText(event.target.value)}
                    placeholder="Cole aqui a descrição da vaga, com requisitos e diferenciais."
                  />
                </Field>
              </>
            )}
          </fieldset>

          <div>
            <Button type="submit" isLoading={submitMutation.isPending}>
              {submitMutation.isPending ? null : (
                <DocumentMagnifyingGlassIcon className="size-4" aria-hidden="true" />
              )}
              Analisar vaga
            </Button>
          </div>
        </Card>
      </form>

      <div className="mt-md">
        <Alert variant="info">
          Se este par currículo e vaga já foi analisado, o resultado anterior é reaproveitado sem
          nova chamada de IA.
        </Alert>
      </div>
    </>
  );
}
