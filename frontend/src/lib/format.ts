import type { Seniority, WorkModel } from "../types/api";

const dateFormatter = new Intl.DateTimeFormat("pt-BR", { dateStyle: "short" });
const dateTimeFormatter = new Intl.DateTimeFormat("pt-BR", {
  dateStyle: "short",
  timeStyle: "short",
});

function parseDate(value: string): Date | null {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

export function formatDate(value: string): string {
  const date = parseDate(value);
  return date ? dateFormatter.format(date) : "Data indisponível";
}

export function formatDateTime(value: string): string {
  const date = parseDate(value);
  return date ? dateTimeFormatter.format(date) : "Data indisponível";
}

export function formatChunkCount(count: number): string {
  return `${count} ${count === 1 ? "trecho" : "trechos"}`;
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} KB`;
  return `${(bytes / (1024 * 1024)).toLocaleString("pt-BR", { maximumFractionDigits: 1 })} MB`;
}

export const SENIORITY_LABELS: Record<Seniority, string> = {
  intern: "Estágio",
  junior: "Júnior",
  mid: "Pleno",
  senior: "Sênior",
  lead: "Liderança",
  unspecified: "Não informada",
};

export const WORK_MODEL_LABELS: Record<WorkModel, string> = {
  remote: "Remoto",
  hybrid: "Híbrido",
  onsite: "Presencial",
  unspecified: "Não informado",
};
