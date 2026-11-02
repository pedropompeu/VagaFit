import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { createJob } from "../api/jobs";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Field } from "../components/ui/Field";
import { Input } from "../components/ui/Input";
import { PageHeader } from "../components/ui/PageHeader";
import { Textarea } from "../components/ui/Textarea";
import { getApiErrorMessage } from "../lib/errors";
import { usePageTitle } from "../lib/usePageTitle";

const MAX_JOB_TEXT = 30_000;
const MIN_JOB_TEXT = 20;

export function NewJobPage() {
  usePageTitle("Colar vaga");

  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [company, setCompany] = useState("");
  const [rawText, setRawText] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const createMutation = useMutation({
    mutationFn: createJob,
    onSuccess: (job) => {
      void queryClient.invalidateQueries({ queryKey: ["jobs"], exact: true });
      navigate(`/vagas/${job.id}`);
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setFormError(null);

    const trimmedText = rawText.trim();
    if (trimmedText.length < MIN_JOB_TEXT) {
      setFormError("Cole o texto da vaga com pelo menos 20 caracteres.");
      return;
    }

    const trimmedTitle = title.trim();
    const trimmedCompany = company.trim();

    createMutation.mutate({
      raw_text: trimmedText,
      title: trimmedTitle.length > 0 ? trimmedTitle : undefined,
      company: trimmedCompany.length > 0 ? trimmedCompany : undefined,
    });
  }

  const error =
    formError ?? (createMutation.isError ? getApiErrorMessage(createMutation.error) : null);

  return (
    <>
      <PageHeader
        backTo="/vagas"
        backLabel="Vagas"
        title="Colar vaga"
        description="Cole o texto completo da vaga. O VagaFit extrai os requisitos e você confere a lista antes de analisar."
      />

      <form onSubmit={handleSubmit} className="flex flex-col gap-lg">
        {error ? <Alert variant="error">{error}</Alert> : null}

        <Card className="flex flex-col gap-md p-lg">
          <div className="grid gap-md sm:grid-cols-2">
            <Field
              label="Cargo"
              htmlFor="job-title"
              hint="Opcional. Se ficar em branco, usamos a primeira linha do texto."
            >
              <Input
                id="job-title"
                name="title"
                maxLength={160}
                value={title}
                onChange={(event) => {
                  setTitle(event.target.value);
                  setFormError(null);
                }}
                placeholder="Ex.: Pessoa Desenvolvedora Backend"
              />
            </Field>

            <Field label="Empresa" htmlFor="job-company" hint="Opcional.">
              <Input
                id="job-company"
                name="company"
                maxLength={160}
                value={company}
                onChange={(event) => {
                  setCompany(event.target.value);
                  setFormError(null);
                }}
                placeholder="Ex.: Acme"
              />
            </Field>
          </div>

          <Field
            label="Texto da vaga"
            htmlFor="job-raw-text"
            required
            hint={`${rawText.length.toLocaleString("pt-BR")} de ${MAX_JOB_TEXT.toLocaleString("pt-BR")} caracteres · mínimo de ${MIN_JOB_TEXT}`}
          >
            <Textarea
              id="job-raw-text"
              name="raw_text"
              required
              minLength={MIN_JOB_TEXT}
              maxLength={MAX_JOB_TEXT}
              rows={12}
              aria-describedby="job-raw-text-hint"
              value={rawText}
              onChange={(event) => {
                setRawText(event.target.value);
                setFormError(null);
              }}
              placeholder="Cole aqui a descrição da vaga, incluindo requisitos e diferenciais."
            />
          </Field>

          <div>
            <Button type="submit" isLoading={createMutation.isPending}>
              Salvar vaga
            </Button>
          </div>
        </Card>
      </form>

      <div className="mt-md">
        <Alert variant="info">
          A extração de requisitos roda em segundo plano. Você pode continuar usando o VagaFit
          enquanto a vaga é processada.
        </Alert>
      </div>
    </>
  );
}
