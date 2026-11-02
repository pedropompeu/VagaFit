import { ArrowUpTrayIcon } from "@heroicons/react/24/outline";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState, type ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";

import { createResume, previewResume, type ResumeContentInput } from "../api/resumes";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Field } from "../components/ui/Field";
import { Input } from "../components/ui/Input";
import { PageHeader } from "../components/ui/PageHeader";
import { Textarea } from "../components/ui/Textarea";
import { cn } from "../lib/cn";
import { getApiErrorMessage } from "../lib/errors";
import { formatChunkCount, formatFileSize } from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";
import type { ResumePreview } from "../types/api";

const MAX_FILE_BYTES = 5 * 1024 * 1024;

type ContentMode = "text" | "file";

function modeButtonClass(active: boolean): string {
  return cn(
    "rounded-md border px-sm py-xs text-sm font-medium transition-colors",
    active
      ? "border-brand bg-brand-soft text-brand"
      : "border-line bg-surface text-muted hover:text-brand",
  );
}

export function NewResumePage() {
  usePageTitle("Adicionar currículo");

  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [title, setTitle] = useState("");
  const [mode, setMode] = useState<ContentMode>("text");
  const [text, setText] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [fileError, setFileError] = useState<string | null>(null);
  const [preview, setPreview] = useState<ResumePreview | null>(null);

  const previewMutation = useMutation({
    mutationFn: previewResume,
    onSuccess: (data) => setPreview(data),
  });

  const createMutation = useMutation({
    mutationFn: createResume,
    onSuccess: (resume) => {
      void queryClient.invalidateQueries({ queryKey: ["resumes"], exact: true });
      navigate(`/curriculos/${resume.id}`);
    },
  });

  function resetFeedback() {
    setFormError(null);
    setPreview(null);
    previewMutation.reset();
    createMutation.reset();
  }

  function handleModeChange(nextMode: ContentMode) {
    if (nextMode === mode) return;
    setMode(nextMode);
    setFileError(null);
    resetFeedback();
  }

  function handleTextChange(value: string) {
    setText(value);
    resetFeedback();
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0] ?? null;
    setFileError(null);
    resetFeedback();

    if (!selected) {
      setFile(null);
      return;
    }

    const isPdf =
      selected.type === "application/pdf" || selected.name.toLowerCase().endsWith(".pdf");
    if (!isPdf) {
      setFile(null);
      event.target.value = "";
      setFileError("Envie um arquivo PDF.");
      return;
    }
    if (selected.size > MAX_FILE_BYTES) {
      setFile(null);
      event.target.value = "";
      setFileError("O arquivo passa do limite de 5 MB.");
      return;
    }
    setFile(selected);
  }

  function validateContent(): ResumeContentInput | null {
    if (mode === "file") {
      if (!file) {
        setFormError("Selecione um arquivo PDF.");
        return null;
      }
      return { file };
    }

    const trimmed = text.trim();
    if (trimmed.length === 0) {
      setFormError("Cole o texto do currículo.");
      return null;
    }
    return { text: trimmed };
  }

  function handlePreview() {
    const content = validateContent();
    if (!content) return;
    previewMutation.mutate(content);
  }

  function handleSave() {
    const content = validateContent();
    if (!content) return;

    const trimmedTitle = title.trim();
    if (trimmedTitle.length === 0) {
      setFormError("Dê um título ao currículo.");
      return;
    }

    createMutation.mutate({ title: trimmedTitle, ...content });
  }

  const actionError =
    formError ??
    (createMutation.isError
      ? getApiErrorMessage(createMutation.error)
      : previewMutation.isError
        ? getApiErrorMessage(previewMutation.error)
        : null);

  return (
    <>
      <PageHeader
        backTo="/curriculos"
        backLabel="Currículos"
        title="Adicionar currículo"
        description="Cole o texto ou envie um PDF. Você pode conferir a divisão em trechos antes de salvar."
      />

      <form
        onSubmit={(event) => {
          event.preventDefault();
          handleSave();
        }}
        className="flex flex-col gap-lg"
      >
        {actionError ? <Alert variant="error">{actionError}</Alert> : null}

        <Card className="flex flex-col gap-md p-lg">
          <Field
            label="Título"
            htmlFor="resume-title"
            required
            hint="Um nome para reconhecer este currículo depois."
          >
            <Input
              id="resume-title"
              name="title"
              required
              maxLength={120}
              value={title}
              onChange={(event) => {
                setTitle(event.target.value);
                setFormError(null);
              }}
              placeholder="Ex.: Currículo backend 2026"
            />
          </Field>

          <div className="flex flex-col gap-2xs">
            <span className="text-sm font-medium text-ink">Forma de envio</span>
            <div role="group" aria-label="Forma de envio" className="flex flex-wrap gap-xs">
              <button
                type="button"
                aria-pressed={mode === "text"}
                className={modeButtonClass(mode === "text")}
                onClick={() => handleModeChange("text")}
              >
                Colar texto
              </button>
              <button
                type="button"
                aria-pressed={mode === "file"}
                className={modeButtonClass(mode === "file")}
                onClick={() => handleModeChange("file")}
              >
                <ArrowUpTrayIcon className="size-4" aria-hidden="true" />
                Enviar PDF
              </button>
            </div>
          </div>

          {mode === "text" ? (
            <Field
              label="Texto do currículo"
              htmlFor="resume-text"
              required
              hint={`${text.length.toLocaleString("pt-BR")} caracteres`}
            >
              <Textarea
                id="resume-text"
                name="text"
                className="min-h-64"
                aria-describedby="resume-text-hint"
                value={text}
                onChange={(event) => handleTextChange(event.target.value)}
                placeholder="Cole aqui o conteúdo do currículo."
              />
            </Field>
          ) : (
            <Field
              label="Arquivo PDF"
              htmlFor="resume-file"
              required
              error={fileError}
              hint="PDF de até 5 MB."
            >
              <input
                id="resume-file"
                name="file"
                type="file"
                accept="application/pdf,.pdf"
                aria-describedby={fileError ? "resume-file-error" : "resume-file-hint"}
                onChange={handleFileChange}
                className={cn(
                  "block w-full cursor-pointer rounded-md border border-line bg-surface text-sm text-muted",
                  "file:mr-sm file:cursor-pointer file:border-0 file:bg-brand-soft file:px-sm file:py-xs file:text-sm file:font-medium file:text-brand",
                  fileError && "border-danger",
                )}
              />
              {file ? (
                <p className="text-sm text-muted">
                  {file.name} · {formatFileSize(file.size)}
                </p>
              ) : null}
            </Field>
          )}

          <div className="flex flex-wrap gap-xs">
            <Button
              type="button"
              variant="secondary"
              onClick={handlePreview}
              isLoading={previewMutation.isPending}
              disabled={createMutation.isPending}
            >
              Pré-visualizar divisão
            </Button>
            <Button type="submit" isLoading={createMutation.isPending} disabled={previewMutation.isPending}>
              Salvar currículo
            </Button>
          </div>
        </Card>
      </form>

      {preview ? (
        <section aria-labelledby="preview-title" className="mt-lg">
          <div className="mb-sm flex flex-wrap items-center justify-between gap-xs">
            <h2 id="preview-title" className="text-lg font-semibold text-ink">
              Prévia da divisão
            </h2>
            <p className="text-sm text-muted">{formatChunkCount(preview.chunk_count)}</p>
          </div>
          <p className="mb-md text-sm text-muted">
            Nada foi salvo ainda. Confira como o texto será dividido antes de continuar.
          </p>

          {preview.chunks.length === 0 ? (
            <Alert variant="warning">Nenhum trecho foi gerado para este conteúdo.</Alert>
          ) : (
            <ol className="flex flex-col gap-sm">
              {preview.chunks.map((chunk) => (
                <li key={chunk.ordinal}>
                  <Card className="p-md">
                    <div className="mb-2xs flex flex-wrap items-center justify-between gap-xs">
                      <span className="text-sm font-medium text-ink">
                        Trecho {chunk.ordinal + 1}
                      </span>
                      <span className="text-xs text-muted">
                        ~{chunk.estimated_tokens.toLocaleString("pt-BR")} tokens
                      </span>
                    </div>
                    <p className="max-h-48 overflow-y-auto whitespace-pre-wrap text-sm text-muted">
                      {chunk.content}
                    </p>
                  </Card>
                </li>
              ))}
            </ol>
          )}
        </section>
      ) : null}
    </>
  );
}
