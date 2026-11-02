import type { SVGProps } from "react";

/**
 * Três ícones próprios no grid 24 e traço 1,5 do Heroicons (BRAND.md, seção 07).
 * O Heroicons não tem "sem evidência", "citação" e "grifo"; os substitutos dele dizem outra coisa.
 */
const base = {
  viewBox: "0 0 24 24",
  fill: "none",
  stroke: "currentColor",
  strokeWidth: 1.5,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  "aria-hidden": true,
  focusable: false,
} as const;

type IconProps = SVGProps<SVGSVGElement>;

/** Sem evidência: círculo tracejado (repete a borda do badge) com um traço no meio. */
export function NoEvidenceIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <circle cx="12" cy="12" r="9" strokeDasharray="1.6 3.1" />
      <path d="M9 12h6" />
    </svg>
  );
}

/** Citação: aspas em bloco. */
export function QuoteIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M6.75 8.25h3.5v3.5h-3.5zM10.25 11.75c0 2.5-1.25 3.75-3.5 4.25M14.25 8.25h3.5v3.5h-3.5zM17.75 11.75c0 2.5-1.25 3.75-3.5 4.25" />
    </svg>
  );
}

/** Grifo: linha marcada entre duas linhas de texto. Só em legenda ou ajuda, nunca em botão. */
export function HighlightIcon(props: IconProps) {
  return (
    <svg {...base} {...props}>
      <path d="M4.5 6h15M4.5 18h9" />
      <rect x="3.75" y="9.25" width="16.5" height="5.5" rx="1.25" />
      <path d="M6.75 12h10.5" />
    </svg>
  );
}
