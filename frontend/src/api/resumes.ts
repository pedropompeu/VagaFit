import type { ResumeDetail, ResumePreview, ResumeSummary } from "../types/api";
import { api } from "./client";

export interface ResumeContentInput {
  text?: string;
  file?: File;
}

export interface CreateResumeInput extends ResumeContentInput {
  title: string;
}

function buildContentForm(input: ResumeContentInput): FormData {
  const form = new FormData();
  if (input.file) {
    form.append("file", input.file);
  } else if (input.text !== undefined) {
    form.append("text", input.text);
  }
  return form;
}

export async function listResumes(): Promise<ResumeSummary[]> {
  const { data } = await api.get<ResumeSummary[]>("/resumes");
  return data;
}

export async function getResume(id: string): Promise<ResumeDetail> {
  const { data } = await api.get<ResumeDetail>(`/resumes/${id}`);
  return data;
}

export async function createResume(input: CreateResumeInput): Promise<ResumeSummary> {
  const form = buildContentForm(input);
  form.append("title", input.title);
  const { data } = await api.post<ResumeSummary>("/resumes", form);
  return data;
}

export async function previewResume(input: ResumeContentInput): Promise<ResumePreview> {
  const { data } = await api.post<ResumePreview>("/resumes/preview", buildContentForm(input));
  return data;
}

export async function deleteResume(id: string): Promise<void> {
  await api.delete(`/resumes/${id}`);
}
