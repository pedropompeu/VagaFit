import type { Evidence, ResumeChunk } from "../../types/api";
import { EvidenceQuote } from "./EvidenceQuote";

interface EvidenceListProps {
  evidence: Evidence[];
  chunks: Map<string, ResumeChunk>;
}

/** Lista de citações do currículo; cada uma traz o trecho completo num `<details>`. */
export function EvidenceList({ evidence, chunks }: EvidenceListProps) {
  return (
    <ul className="flex flex-col gap-xs">
      {evidence.map((item, index) => (
        <li key={`${item.chunk_id}-${index}`}>
          <EvidenceQuote quote={item.quote} chunk={chunks.get(item.chunk_id)} />
        </li>
      ))}
    </ul>
  );
}
