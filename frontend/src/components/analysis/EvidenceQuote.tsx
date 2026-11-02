import { ChevronDownIcon } from "@heroicons/react/24/outline";
import type { ReactNode } from "react";

import type { ResumeChunk } from "../../types/api";

const MARK = "bg-evidence-bg text-evidence-text [box-decoration-break:clone] [-webkit-box-decoration-break:clone]";

/** No trecho completo, a citação continua com o marca-texto. Se não achar o texto exato, mostra sem marca. */
function withHighlight(content: string, quote: string): ReactNode {
  const start = quote ? content.indexOf(quote) : -1;
  if (start < 0) return content;
  return (
    <>
      {content.slice(0, start)}
      <mark className={MARK}>{quote}</mark>
      {content.slice(start + quote.length)}
    </>
  );
}

interface EvidenceQuoteProps {
  quote: string;
  /** Trecho do currículo de onde a citação saiu. Ausente enquanto o currículo não carregou. */
  chunk?: ResumeChunk;
}

/**
 * Citação do currículo (BRAND.md 8.6): bloco âmbar com faixa lateral, texto em mono com marca-texto,
 * legenda "Currículo · trecho N" e o trecho completo num `<details>`. Nunca mostra o UUID do trecho.
 */
export function EvidenceQuote({ quote, chunk }: EvidenceQuoteProps) {
  const number = chunk ? chunk.ordinal + 1 : null;

  return (
    <figure className="max-w-measure rounded-r-md border-l-[3px] border-evidence-border bg-evidence-soft px-sm py-xs">
      <blockquote className="font-mono text-mono-sm text-evidence-text">
        <mark className={MARK}>“{quote}”</mark>
      </blockquote>
      <figcaption className="mt-2xs font-mono text-mono-sm text-evidence-meta">
        {number === null ? "Currículo" : `Currículo · trecho ${number}`}
      </figcaption>
      {chunk ? (
        <details className="group mt-xs">
          <summary className="inline-flex cursor-pointer list-none items-center gap-2xs rounded-sm text-label font-medium text-brand transition-colors hover:text-brand-hover hover:underline active:text-brand-active [&::-webkit-details-marker]:hidden">
            Ver trecho {number} completo
            <ChevronDownIcon
              className="size-4 transition-transform duration-base group-open:rotate-180"
              aria-hidden="true"
            />
          </summary>
          <p className="mt-xs whitespace-pre-wrap rounded-md border border-line bg-sunken p-sm font-mono text-mono-sm text-muted">
            {withHighlight(chunk.content, quote)}
          </p>
        </details>
      ) : null}
    </figure>
  );
}
