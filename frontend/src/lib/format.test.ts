import { describe, expect, it } from "vitest";

import {
  countWithEvidence,
  formatChunkCount,
  formatEvidenceCount,
  formatDate,
  formatFileSize,
  formatPercent,
  formatPlainDate,
} from "./format";

describe("formatPlainDate", () => {
  it("vira dd/mm/aaaa sem deslocar o dia pelo fuso", () => {
    expect(formatPlainDate("2026-01-01")).toBe("01/01/2026");
  });

  it("recusa formato inesperado", () => {
    expect(formatPlainDate("01/01/2026")).toBe("Data indisponível");
  });
});

describe("formatDate", () => {
  it("avisa quando a data não é válida", () => {
    expect(formatDate("não é data")).toBe("Data indisponível");
  });
});

describe("formatFileSize", () => {
  it("escolhe a unidade", () => {
    expect(formatFileSize(512)).toBe("512 B");
    expect(formatFileSize(1536)).toBe("1,5 KB");
    expect(formatFileSize(5 * 1024 * 1024)).toBe("5 MB");
  });
});

describe("textos curtos", () => {
  it("flexiona trecho e arredonda porcentagem", () => {
    expect(formatChunkCount(1)).toBe("1 trecho");
    expect(formatChunkCount(3)).toBe("3 trechos");
    expect(formatPercent(0.666)).toBe("67%");
  });
});

describe("countWithEvidence", () => {
  const reqs = [
    { kind: "required" as const, evidence: [{}] },
    { kind: "required" as const, evidence: [{}, {}] },
    { kind: "required" as const, evidence: [] },
    { kind: "nice_to_have" as const, evidence: [] },
  ];

  it("conta só os requisitos do grupo que têm citação", () => {
    expect(countWithEvidence(reqs, "required")).toEqual({ withEvidence: 2, total: 3 });
    expect(countWithEvidence(reqs, "nice_to_have")).toEqual({ withEvidence: 0, total: 1 });
  });

  it("escreve a contagem no formato do BRAND", () => {
    expect(formatEvidenceCount(4, 6)).toBe("4 de 6 com evidência");
  });
});
