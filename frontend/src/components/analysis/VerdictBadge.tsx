import { CheckCircleIcon, MinusCircleIcon, XCircleIcon } from "@heroicons/react/24/outline";
import type { ComponentType, SVGProps } from "react";

import { cn } from "../../lib/cn";
import type { Verdict } from "../../types/api";
import { NoEvidenceIcon } from "../icons";

type VerdictView = "met" | "partial" | "not-met" | "no-evidence";

/* Classes completas, sem template: o Tailwind só gera o que encontra escrito no código. */
const VIEW: Record<VerdictView, { label: string; Icon: ComponentType<SVGProps<SVGSVGElement>>; className: string }> = {
  met: {
    label: "Atende",
    Icon: CheckCircleIcon,
    className: "border-verdict-met-border bg-verdict-met-bg text-verdict-met-text",
  },
  partial: {
    label: "Atende em parte",
    Icon: MinusCircleIcon,
    className: "border-verdict-partial-border bg-verdict-partial-bg text-verdict-partial-text",
  },
  "not-met": {
    label: "Não atende",
    Icon: XCircleIcon,
    className: "border-verdict-not-met-border bg-verdict-not-met-bg text-verdict-not-met-text",
  },
  "no-evidence": {
    label: "Sem evidência",
    Icon: NoEvidenceIcon,
    className:
      "border-dashed border-verdict-no-evidence-border bg-verdict-no-evidence-bg text-verdict-no-evidence-text",
  },
};

interface VerdictBadgeProps {
  verdict: Verdict;
  /** "Atende" só aparece com citação do currículo; sem ela, o badge vira "Sem evidência". */
  hasEvidence: boolean;
  className?: string;
}

/** Veredito do requisito, sempre com ícone e texto (BRAND.md 3.3 e 8.4). Quem decide é o dado, não a cor. */
export function VerdictBadge({ verdict, hasEvidence, className }: VerdictBadgeProps) {
  const key: VerdictView =
    verdict === "met" ? (hasEvidence ? "met" : "no-evidence") : verdict === "partial" ? "partial" : "not-met";
  const { label, Icon, className: toneClass } = VIEW[key];

  return (
    <span
      className={cn(
        "inline-flex shrink-0 items-center gap-2xs rounded-sm border px-xs py-2xs text-xs font-medium",
        toneClass,
        className,
      )}
    >
      <Icon className="size-4" aria-hidden="true" />
      {label}
    </span>
  );
}
