import type { JobDetail, JobSummary } from "../types/api";
import { api } from "./client";

export interface CreateJobInput {
  raw_text: string;
  title?: string;
  company?: string;
}

export async function listJobs(): Promise<JobSummary[]> {
  const { data } = await api.get<JobSummary[]>("/jobs");
  return data;
}

export async function getJob(id: string): Promise<JobDetail> {
  const { data } = await api.get<JobDetail>(`/jobs/${id}`);
  return data;
}

export async function createJob(input: CreateJobInput): Promise<JobSummary> {
  const { data } = await api.post<JobSummary>("/jobs", input);
  return data;
}

export async function deleteJob(id: string): Promise<void> {
  await api.delete(`/jobs/${id}`);
}
