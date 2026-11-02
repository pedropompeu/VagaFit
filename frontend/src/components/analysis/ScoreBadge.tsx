import { cn } from "../../lib/cn";

interface ScoreBadgeProps {
  score: number | null;
  /** "md" para listas; "lg" para o cabeçalho do resultado. Nos dois, a cor não muda por faixa. */
  size?: "md" | "lg";
  /** Mostra "Score de aderência" acima do número. Sem ele, o rótulo fica só para leitores de tela. */
  showLabel?: boolean;
  className?: string;
}

/** Score neutro (BRAND.md 8.5): `72/100` em mono, nunca semáforo, anel ou gauge. */
export function ScoreBadge({ score, size = "md", showLabel = false, className }: ScoreBadgeProps) {
  const accessibleLabel =
    score === null ? "Score de aderência: indisponível" : `Score de aderência: ${score} de 100`;

  const badge = (
    <span
      role="img"
      aria-label={accessibleLabel}
      className={cn(
        "inline-flex items-baseline rounded-sm border font-mono font-medium tabular-nums",
        size === "lg" ? "px-sm py-2xs text-2xl" : "px-xs py-2xs text-mono-sm",
        score === null
          ? "border-dashed border-verdict-no-evidence-border bg-verdict-no-evidence-bg text-verdict-no-evidence-text"
          : "border-score-border bg-score-bg text-score-text",
      )}
    >
      {score === null ? "—" : score}/100
    </span>
  );

  if (!showLabel) return <span className={className}>{badge}</span>;

  return (
    <div className={cn("flex flex-col items-start gap-2xs", className)}>
      <span aria-hidden="true" className="text-caption text-muted">
        Score de aderência
      </span>
      {badge}
    </div>
  );
}
