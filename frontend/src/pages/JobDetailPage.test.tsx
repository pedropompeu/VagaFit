import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { getJob, retryJobExtraction } from "../api/jobs";
import type { JobDetail } from "../types/api";
import { ROUTER_FUTURE } from "../test/router";
import { JobDetailPage } from "./JobDetailPage";

vi.mock("../api/jobs", () => ({
  getJob: vi.fn(),
  retryJobExtraction: vi.fn(),
  deleteJob: vi.fn(),
}));

const JOB: JobDetail = {
  id: "job-1",
  title: "Backend Python",
  company: "Acme",
  created_at: "2026-11-07T12:00:00Z",
  extraction_status: "failed",
  raw_text: "Texto da vaga",
  extracted: null,
};

function renderPage() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={client}>
      <MemoryRouter initialEntries={["/vagas/job-1"]} future={ROUTER_FUTURE}>
        <Routes>
          <Route path="/vagas/:jobId" element={<JobDetailPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("JobDetailPage com extração em falha", () => {
  beforeEach(() => {
    vi.mocked(getJob).mockReset();
    vi.mocked(retryJobExtraction).mockReset();
  });

  it("mostra o aviso de falha, sem o aviso de 'nenhum requisito', e reenvia a extração", async () => {
    vi.mocked(getJob).mockResolvedValue(JOB);
    vi.mocked(retryJobExtraction).mockResolvedValue({ ...JOB, extraction_status: "pending" });
    renderPage();

    expect(await screen.findByText("Não foi possível extrair os requisitos")).toBeTruthy();
    expect(screen.queryByText(/nenhum requisito foi retornado/)).toBeNull();

    await userEvent.setup().click(screen.getByRole("button", { name: "Tentar de novo" }));

    expect(retryJobExtraction).toHaveBeenCalledWith("job-1");
  });
});
