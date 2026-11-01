import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import type { ResumeChunk } from "../../types/api";
import { EvidenceList } from "./EvidenceList";

const chunk: ResumeChunk = {
  id: "c1",
  ordinal: 0,
  content: "Construí APIs REST em Python com FastAPI.",
};

describe("EvidenceList", () => {
  it("mostra a citação e o trecho completo do currículo", () => {
    render(
      <EvidenceList
        evidence={[{ chunk_id: "c1", quote: "APIs REST em Python" }]}
        chunks={new Map([["c1", chunk]])}
      />,
    );

    expect(screen.getByText("“APIs REST em Python”")).toBeTruthy();
    expect(screen.getByText("Ver trecho 1 do currículo")).toBeTruthy();
    expect(screen.getByText(chunk.content)).toBeTruthy();
  });

  it("mostra a citação mesmo sem o trecho carregado", () => {
    render(<EvidenceList evidence={[{ chunk_id: "x", quote: "Docker" }]} chunks={new Map()} />);

    expect(screen.getByText("“Docker”")).toBeTruthy();
    expect(screen.queryByText(/Ver trecho/)).toBeNull();
  });
});
