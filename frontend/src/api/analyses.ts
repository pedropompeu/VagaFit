import type {
  AnalysisCreated,
  AnalysisDetail,
  AnalysisSummary,
  ScreeningAnswer,
} from "../types/api";
import { api } from "./client";

export async function listAnalyses(jobId?: string): Promise<AnalysisSummary[]> {
  const { data } = await api.get<AnalysisSummary[]>("/analyses", {
    params: jobId ? { job_id: jobId } : undefined,
  });
  return data;
}

export async function getAnalysis(id: string): Promise<AnalysisDetail> {
  const { data } = await api.get<AnalysisDetail>(`/analyses/${id}`);
  return data;
}

export async function createAnalysis(input: {
  resume_id: string;
  job_id: string;
}): Promise<AnalysisCreated> {
  const { data } = await api.post<AnalysisCreated>("/analyses", input);
  return data;
}

export async function listScreening(analysisId: string): Promise<ScreeningAnswer[]> {
  const { data } = await api.get<ScreeningAnswer[]>(`/analyses/${analysisId}/screening`);
  return data;
}

export async function createScreening(
  analysisId: string,
  questions: string[],
): Promise<ScreeningAnswer[]> {
  const { data } = await api.post<ScreeningAnswer[]>(`/analyses/${analysisId}/screening`, {
    questions,
  });
  return data;
}
