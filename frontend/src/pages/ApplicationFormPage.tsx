import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { useState, type FormEvent } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";

import { listAnalyses } from "../api/analyses";
import {
  createApplication,
  getApplication,
  updateApplication,
  type ApplicationInput,
  type ApplicationPatch,
} from "../api/applications";
import { listJobs } from "../api/jobs";
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
import { getApiErrorMessage } from "../lib/errors";
import {
  ANALYSIS_STATUS_LABELS,
  APPLICATION_STATUS_LABELS,
  formatDateTime,
  todayPlainDate,
} from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";
import { APPLICATION_STATUSES, type Application, type ApplicationStatus } from "../types/api";

interface FormValues {
  jobId: string;
  analysisId: string;
  status: ApplicationStatus;
  platform: string;
  salary: string;
  nextStep: string;
  appliedAt: string;
}

function valuesFrom(application: Application): FormValues {
  return {
    jobId: application.job.id,
    analysisId: application.analysis_id ?? "",
    status: application.status,
    platform: application.platform ?? "",
    salary: application.salary_expectation?.toString() ?? "",
    nextStep: application.next_step ?? "",
    appliedAt: application.applied_at,
  };
}

function conflictStatus(error: unknown): number | undefined {
  return axios.isAxiosError(error) ? error.response?.status : undefined;
}

interface ApplicationFormProps {
  initial: FormValues;
  editing: Application | null;
}

function ApplicationForm({ initial, editing }: ApplicationFormProps) {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [values, setValues] = useState<FormValues>(initial);
  const [formError, setFormError] = useState<string | null>(null);

  const jobsQuery = useQuery({ queryKey: ["jobs"], queryFn: listJobs, enabled: !editing });
  const analysesQuery = useQuery({
    queryKey: ["analyses", "list", values.jobId],
    queryFn: () => listAnalyses(values.jobId),
    enabled: Boolean(values.jobId),
  });
  const analyses = analysesQuery.data ?? [];

  const mutation = useMutation({
    mutationFn: (payload: { create?: ApplicationInput; patch?: ApplicationPatch }) =>
      editing && payload.patch
        ? updateApplication(editing.id, payload.patch)
        : createApplication(payload.create!),
    onSuccess: (application) => {
      void queryClient.invalidateQueries({ queryKey: ["applications"] });
      queryClient.setQueryData(["applications", "detail", application.id], application);
      navigate("/candidaturas");
    },
  });

  function set<K extends keyof FormValues>(key: K, value: FormValues[K]) {
    setValues((current) => ({ ...current, [key]: value }));
    setFormError(null);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!values.jobId) {
      setFormError("Escolha a vaga.");
      return;
    }
    const salaryText = values.salary.trim();
    const salary = salaryText === "" ? null : Number(salaryText);
    if (salary !== null && (!Number.isInteger(salary) || salary < 0)) {
      setFormError("A pretensão salarial precisa ser um valor inteiro em reais.");
      return;
    }
    if (!values.appliedAt) {
      setFormError("Informe a data da candidatura.");
      return;
    }

    const platform = values.platform.trim() || null;
    const nextStep = values.nextStep.trim() || null;
    const analysisId = values.analysisId || null;

    if (editing) {
      // PATCH completo dos campos editáveis: `null` limpa o que foi apagado no formulário.
      mutation.mutate({
        patch: {
          analysis_id: analysisId,
          status: values.status,
          platform,
          salary_expectation: salary,
          next_step: nextStep,
          applied_at: values.appliedAt,
        },
      });
      return;
    }
    mutation.mutate({
      create: {
        job_id: values.jobId,
        status: values.status,
        applied_at: values.appliedAt,
        ...(analysisId ? { analysis_id: analysisId } : {}),
        ...(platform ? { platform } : {}),
        ...(salary !== null ? { salary_expectation: salary } : {}),
        ...(nextStep ? { next_step: nextStep } : {}),
      },
    });
  }

  const status = conflictStatus(mutation.error);
  const apiError = mutation.isError ? getApiErrorMessage(mutation.error) : null;
  const jobs = jobsQuery.data ?? [];

  if (!editing && jobsQuery.isLoading) return <PageLoader label="Carregando vagas…" />;
  if (!editing && jobsQuery.isError) {
    return (
      <ErrorState
        description={getApiErrorMessage(jobsQuery.error)}
        onRetry={() => void jobsQuery.refetch()}
      />
    );
  }
  if (!editing && jobs.length === 0) {
    return (
      <EmptyState
        title="Cadastre uma vaga primeiro"
        description="A candidatura fica ligada a uma vaga cadastrada no VagaFit."
        action={<LinkButton to="/vagas/nova">Cadastrar vaga</LinkButton>}
      />
    );
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-lg">
      {formError ? <Alert variant="error">{formError}</Alert> : null}
      {apiError ? (
        <Alert
          variant="error"
          title={
            status === 409
              ? "Esta vaga já tem candidatura"
              : status === 422
                ? "Não deu para salvar"
                : undefined
          }
        >
          <p>{apiError}</p>
          {status === 409 ? (
            <p className="mt-2xs">
              <Link to="/candidaturas" className="font-medium underline">
                Ver candidaturas
              </Link>{" "}
              para editar a que já existe.
            </p>
          ) : null}
        </Alert>
      ) : null}

      <Card className="flex flex-col gap-md p-lg">
        <Field label="Vaga" htmlFor="application-job" required>
          {editing ? (
            <Input
              id="application-job"
              value={
                editing.job.company ? `${editing.job.title} · ${editing.job.company}` : editing.job.title
              }
              disabled
            />
          ) : (
            <Select
              id="application-job"
              value={values.jobId}
              onChange={(event) => {
                set("jobId", event.target.value);
                set("analysisId", "");
              }}
            >
              <option value="">Escolha a vaga</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.company ? `${job.title} · ${job.company}` : job.title}
                </option>
              ))}
            </Select>
          )}
        </Field>

        <Field
          label="Análise usada"
          htmlFor="application-analysis"
          hint="Opcional. Liga a candidatura ao resultado que você consultou."
        >
          <Select
            id="application-analysis"
            aria-describedby="application-analysis-hint"
            value={values.analysisId}
            disabled={!values.jobId || analysesQuery.isLoading}
            onChange={(event) => set("analysisId", event.target.value)}
          >
            <option value="">Nenhuma</option>
            {analyses.map((analysis) => (
              <option key={analysis.id} value={analysis.id}>
                {analysis.status === "done"
                  ? `Score ${analysis.score ?? "–"} · ${formatDateTime(analysis.created_at)}`
                  : `${ANALYSIS_STATUS_LABELS[analysis.status]} · ${formatDateTime(analysis.created_at)}`}
              </option>
            ))}
          </Select>
        </Field>

        <div className="grid gap-md sm:grid-cols-2">
          <Field label="Status" htmlFor="application-status" required>
            <Select
              id="application-status"
              value={values.status}
              onChange={(event) => set("status", event.target.value as ApplicationStatus)}
            >
              {APPLICATION_STATUSES.map((item) => (
                <option key={item} value={item}>
                  {APPLICATION_STATUS_LABELS[item]}
                </option>
              ))}
            </Select>
          </Field>
          <Field label="Data da candidatura" htmlFor="application-date" required>
            <Input
              id="application-date"
              type="date"
              required
              value={values.appliedAt}
              onChange={(event) => set("appliedAt", event.target.value)}
            />
          </Field>
          <Field label="Plataforma" htmlFor="application-platform" hint="Opcional. Ex.: LinkedIn.">
            <Input
              id="application-platform"
              maxLength={60}
              value={values.platform}
              onChange={(event) => set("platform", event.target.value)}
            />
          </Field>
          <Field
            label="Pretensão salarial (R$ por mês)"
            htmlFor="application-salary"
            hint="Opcional. Valor inteiro."
          >
            <Input
              id="application-salary"
              type="number"
              inputMode="numeric"
              min={0}
              max={10_000_000}
              step={1}
              value={values.salary}
              onChange={(event) => set("salary", event.target.value)}
            />
          </Field>
        </div>

        <Field label="Próximo passo" htmlFor="application-next-step" hint="Opcional.">
          <Input
            id="application-next-step"
            maxLength={300}
            value={values.nextStep}
            onChange={(event) => set("nextStep", event.target.value)}
            placeholder="Ex.: Entrevista técnica dia 12"
          />
        </Field>

        <div className="flex flex-wrap gap-xs">
          <Button type="submit" isLoading={mutation.isPending}>
            {editing ? "Salvar alterações" : "Registrar candidatura"}
          </Button>
          <LinkButton to="/candidaturas" variant="ghost">
            Cancelar
          </LinkButton>
        </div>
      </Card>
    </form>
  );
}

export function NewApplicationPage() {
  usePageTitle("Nova candidatura");
  const [searchParams] = useSearchParams();

  return (
    <>
      <PageHeader backTo="/candidaturas" backLabel="Candidaturas" title="Nova candidatura" />
      <ApplicationForm
        editing={null}
        initial={{
          jobId: searchParams.get("vaga") ?? "",
          analysisId: searchParams.get("analise") ?? "",
          status: "sent",
          platform: "",
          salary: "",
          nextStep: "",
          appliedAt: todayPlainDate(),
        }}
      />
    </>
  );
}

export function EditApplicationPage() {
  usePageTitle("Editar candidatura");
  const { applicationId } = useParams<{ applicationId: string }>();

  const query = useQuery({
    queryKey: ["applications", "detail", applicationId ?? ""],
    queryFn: () => getApplication(applicationId ?? ""),
    enabled: Boolean(applicationId),
  });

  const header = (
    <PageHeader backTo="/candidaturas" backLabel="Candidaturas" title="Editar candidatura" />
  );

  if (query.isLoading) {
    return (
      <>
        {header}
        <PageLoader label="Carregando candidatura…" />
      </>
    );
  }
  if (query.isError || !query.data) {
    return (
      <>
        {header}
        <ErrorState
          description={query.isError ? getApiErrorMessage(query.error) : "Candidatura não encontrada."}
          onRetry={() => void query.refetch()}
        />
      </>
    );
  }
  return (
    <>
      {header}
      <ApplicationForm key={query.data.id} editing={query.data} initial={valuesFrom(query.data)} />
    </>
  );
}
