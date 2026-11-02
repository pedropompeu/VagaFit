import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";

import { createScreening, listScreening } from "../../api/analyses";
import { getApiErrorMessage } from "../../lib/errors";
import type { ResumeChunk, ScreeningAnswer } from "../../types/api";
import { Alert } from "../ui/Alert";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Disclosure } from "../ui/Disclosure";
import { Field } from "../ui/Field";
import { Spinner } from "../ui/Spinner";
import { Textarea } from "../ui/Textarea";
import { CopyButton } from "./CopyButton";
import { EvidenceList } from "./EvidenceList";

const MAX_QUESTIONS = 10;
const MIN_QUESTION = 3;
const MAX_QUESTION = 500;

export function parseQuestions(raw: string): string[] {
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}

function validateQuestions(questions: string[]): string | null {
  if (questions.length === 0) return "Escreva pelo menos uma pergunta, uma por linha.";
  if (questions.length > MAX_QUESTIONS) return `Envie no máximo ${MAX_QUESTIONS} perguntas por vez.`;
  const invalid = questions.findIndex(
    (question) => question.length < MIN_QUESTION || question.length > MAX_QUESTION,
  );
  if (invalid >= 0) {
    return `A pergunta da linha ${invalid + 1} precisa ter entre ${MIN_QUESTION} e ${MAX_QUESTION} caracteres.`;
  }
  return null;
}

function AnswerCard({ answer, chunks }: { answer: ScreeningAnswer; chunks: Map<string, ResumeChunk> }) {
  return (
    <Card className={answer.needs_user_input ? "border-warning p-lg" : "p-lg"}>
      <div className="flex flex-wrap items-start justify-between gap-sm">
        <h3 className="min-w-0 flex-1 font-medium text-ink">{answer.question}</h3>
        <div className="flex flex-wrap items-center gap-xs">
          {answer.needs_user_input ? <Badge tone="warning">Precisa da sua resposta</Badge> : null}
          <Badge tone="neutral">Rascunho</Badge>
        </div>
      </div>

      {answer.needs_user_input && answer.user_question ? (
        <Alert variant="warning" className="mt-sm" title="O currículo não responde isto sozinho">
          {answer.user_question}
        </Alert>
      ) : null}

      <p className="mt-sm whitespace-pre-wrap text-sm text-ink">{answer.answer}</p>

      {answer.evidence.length > 0 ? (
        <Disclosure summary={<>Evidências ({answer.evidence.length})</>} className="mt-sm">
          <div className="mt-xs">
            <EvidenceList evidence={answer.evidence} chunks={chunks} />
          </div>
        </Disclosure>
      ) : null}

      <div className="mt-sm">
        <CopyButton text={answer.answer} label="Copiar rascunho" />
      </div>
    </Card>
  );
}

interface ScreeningSectionProps {
  analysisId: string;
  chunks: Map<string, ResumeChunk>;
}

export function ScreeningSection({ analysisId, chunks }: ScreeningSectionProps) {
  const queryClient = useQueryClient();
  const queryKey = ["analyses", "detail", analysisId, "screening"];
  const [raw, setRaw] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const answersQuery = useQuery({ queryKey, queryFn: () => listScreening(analysisId) });

  const mutation = useMutation({
    mutationFn: (questions: string[]) => createScreening(analysisId, questions),
    onSuccess: () => {
      setRaw("");
      void queryClient.invalidateQueries({ queryKey });
    },
  });

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const questions = parseQuestions(raw);
    const problem = validateQuestions(questions);
    setFormError(problem);
    if (!problem) mutation.mutate(questions);
  }

  const answers = answersQuery.data ?? [];
  const error = formError ?? (mutation.isError ? getApiErrorMessage(mutation.error) : null);
  const count = parseQuestions(raw).length;

  return (
    <section aria-labelledby="screening-title" className="flex flex-col gap-md">
      <div>
        <h2 id="screening-title" className="text-lg font-semibold text-ink">
          Perguntas de triagem
        </h2>
        <p className="mt-2xs text-sm text-muted">
          Cole as perguntas do formulário da vaga. As respostas são rascunhos baseados só no seu
          currículo: revise antes de enviar.
        </p>
      </div>

      <Card className="p-lg">
        <form onSubmit={handleSubmit} className="flex flex-col gap-sm">
          {error ? <Alert variant="error">{error}</Alert> : null}
          <Field
            label="Perguntas (uma por linha)"
            htmlFor="screening-questions"
            hint={`${count} de ${MAX_QUESTIONS} perguntas`}
          >
            <Textarea
              id="screening-questions"
              rows={5}
              aria-describedby="screening-questions-hint"
              value={raw}
              onChange={(event) => {
                setRaw(event.target.value);
                setFormError(null);
              }}
              placeholder={"Você tem experiência com filas assíncronas?\nQual sua pretensão salarial?"}
            />
          </Field>
          <div className="flex flex-wrap items-center gap-sm">
            <Button type="submit" isLoading={mutation.isPending}>
              {count === 1 ? "Gerar rascunho de triagem" : "Gerar rascunhos de triagem"}
            </Button>
            {mutation.isPending ? (
              <span className="text-sm text-muted">
                Escrevendo os rascunhos a partir do seu currículo. Pode levar alguns segundos.
              </span>
            ) : null}
          </div>
        </form>
      </Card>

      {answersQuery.isLoading ? (
        <div className="flex items-center gap-xs text-sm text-muted">
          <Spinner className="h-4 w-4" label="" />
          Carregando respostas…
        </div>
      ) : answersQuery.isError ? (
        <Alert variant="error">{getApiErrorMessage(answersQuery.error)}</Alert>
      ) : answers.length === 0 ? (
        <p className="text-sm text-muted">Nenhuma pergunta respondida ainda.</p>
      ) : (
        <ul className="flex flex-col gap-sm">
          {answers.map((answer) => (
            <li key={answer.id}>
              <AnswerCard answer={answer} chunks={chunks} />
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
