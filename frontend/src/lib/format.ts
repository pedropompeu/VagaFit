import type { BadgeTone } from "../components/ui/Badge";
import type {
  AnalysisStatus,
  ApplicationStatus,
  RequirementKind,
  Seniority,
  Verdict,
  WorkModel,
} from "../types/api";

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

/** Data simples `YYYY-MM-DD` (sem fuso): não passa por `new Date`, que deslocaria o dia. */
export function formatPlainDate(value: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  return match ? `${match[3]}/${match[2]}/${match[1]}` : "Data indisponível";
}

/** Hoje no fuso do navegador, no formato `YYYY-MM-DD`. */
export function todayPlainDate(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${now.getFullYear()}-${month}-${day}`;
}

const currencyFormatter = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
  maximumFractionDigits: 0,
});

export function formatCurrency(value: number): string {
  return currencyFormatter.format(value);
}

export function formatPercent(fraction: number): string {
  return `${Math.round(fraction * 100)}%`;
}

export const VERDICT_LABELS: Record<Verdict, string> = {
  met: "Atende",
  partial: "Atende em parte",
  not_met: "Não atende",
};

export const VERDICT_TONES: Record<Verdict, BadgeTone> = {
  met: "success",
  partial: "warning",
  not_met: "danger",
};

export const KIND_LABELS: Record<RequirementKind, string> = {
  required: "Obrigatório",
  nice_to_have: "Diferencial",
};

export const ANALYSIS_STATUS_LABELS: Record<AnalysisStatus, string> = {
  pending: "Na fila",
  running: "Analisando",
  done: "Concluída",
  failed: "Falhou",
};

export const ANALYSIS_STATUS_TONES: Record<AnalysisStatus, BadgeTone> = {
  pending: "warning",
  running: "warning",
  done: "success",
  failed: "danger",
};

export const APPLICATION_STATUS_LABELS: Record<ApplicationStatus, string> = {
  sent: "Enviada",
  in_review: "Em análise",
  tech_test: "Teste técnico",
  interview: "Entrevista",
  offer: "Proposta",
  rejected: "Recusada",
  no_response: "Sem retorno",
};

export const APPLICATION_STATUS_TONES: Record<ApplicationStatus, BadgeTone> = {
  sent: "neutral",
  in_review: "brand",
  tech_test: "brand",
  interview: "brand",
  offer: "success",
  rejected: "danger",
  no_response: "neutral",
};

export function scoreTone(score: number): BadgeTone {
  if (score >= 70) return "success";
  if (score >= 40) return "warning";
  return "danger";
}

const SCORE_TEXT_CLASSES: Record<BadgeTone, string> = {
  success: "text-success",
  warning: "text-warning",
  danger: "text-danger",
  neutral: "text-ink",
  brand: "text-brand",
};

export function scoreTextClass(score: number): string {
  return SCORE_TEXT_CLASSES[scoreTone(score)];
}
