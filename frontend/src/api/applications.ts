import type { Application, ApplicationStatus } from "../types/api";
import { api } from "./client";

export interface ApplicationInput {
  job_id: string;
  analysis_id?: string | null;
  status?: ApplicationStatus;
  platform?: string | null;
  salary_expectation?: number | null;
  next_step?: string | null;
  applied_at?: string;
}

export type ApplicationPatch = Partial<Omit<ApplicationInput, "job_id">>;

export async function listApplications(statuses: ApplicationStatus[] = []): Promise<Application[]> {
  const params = new URLSearchParams();
  for (const status of statuses) params.append("status", status);
  const { data } = await api.get<Application[]>("/applications", { params });
  return data;
}

export async function getApplication(id: string): Promise<Application> {
  const { data } = await api.get<Application>(`/applications/${id}`);
  return data;
}

export async function createApplication(input: ApplicationInput): Promise<Application> {
  const { data } = await api.post<Application>("/applications", input);
  return data;
}

export async function updateApplication(id: string, patch: ApplicationPatch): Promise<Application> {
  const { data } = await api.patch<Application>(`/applications/${id}`, patch);
  return data;
}

export async function deleteApplication(id: string): Promise<void> {
  await api.delete(`/applications/${id}`);
}
