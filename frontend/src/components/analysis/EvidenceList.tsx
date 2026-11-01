import type { Evidence, ResumeChunk } from "../../types/api";

interface EvidenceListProps {
  evidence: Evidence[];
  chunks: Map<string, ResumeChunk>;
}

/** Cada citação aparece entre aspas; o trecho completo do currículo fica num `<details>`. */
export function EvidenceList({ evidence, chunks }: EvidenceListProps) {
  return (
    <ul className="flex flex-col gap-xs">
      {evidence.map((item, index) => {
        const chunk = chunks.get(item.chunk_id);
        return (
          <li key={`${item.chunk_id}-${index}`} className="rounded-md border border-line bg-canvas p-sm">
            <blockquote className="text-sm italic text-ink">“{item.quote}”</blockquote>
            {chunk ? (
              <details className="mt-xs">
                <summary className="cursor-pointer text-xs font-medium text-brand">
                  Ver trecho {chunk.ordinal + 1} do currículo
                </summary>
                <p className="mt-xs whitespace-pre-wrap text-xs text-muted">{chunk.content}</p>
              </details>
            ) : null}
          </li>
        );
      })}
    </ul>
  );
}
