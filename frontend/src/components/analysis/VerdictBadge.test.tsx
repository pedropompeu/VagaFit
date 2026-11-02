import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { ScoreBadge } from "./ScoreBadge";
import { VerdictBadge } from "./VerdictBadge";

describe("VerdictBadge", () => {
  it("mostra Atende só com citação", () => {
    render(<VerdictBadge verdict="met" hasEvidence />);
    expect(screen.getByText("Atende")).toBeTruthy();
  });

  it("troca Atende sem citação por Sem evidência, em borda tracejada", () => {
    render(<VerdictBadge verdict="met" hasEvidence={false} />);
    const badge = screen.getByText("Sem evidência");
    expect(badge.className).toContain("border-dashed");
    expect(screen.queryByText("Atende")).toBeNull();
  });

  it("dá nome às lacunas", () => {
    render(
      <>
        <VerdictBadge verdict="partial" hasEvidence={false} />
        <VerdictBadge verdict="not_met" hasEvidence={false} />
      </>,
    );
    expect(screen.getByText("Atende em parte")).toBeTruthy();
    expect(screen.getByText("Não atende")).toBeTruthy();
  });
});

describe("ScoreBadge", () => {
  it("mostra 72/100 com rótulo acessível e a mesma cor em qualquer faixa", () => {
    const { rerender } = render(<ScoreBadge score={72} showLabel />);
    const high = screen.getByRole("img", { name: "Score de aderência: 72 de 100" });
    expect(high.textContent).toBe("72/100");
    expect(screen.getByText("Score de aderência")).toBeTruthy();
    const highClass = high.className;

    rerender(<ScoreBadge score={12} showLabel />);
    expect(screen.getByRole("img", { name: "Score de aderência: 12 de 100" }).className).toBe(highClass);
  });

  it("mostra —/100 neutro quando não há score", () => {
    render(<ScoreBadge score={null} />);
    const badge = screen.getByRole("img", { name: "Score de aderência: indisponível" });
    expect(badge.textContent).toBe("—/100");
    expect(badge.className).toContain("border-dashed");
  });
});
