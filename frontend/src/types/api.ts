export interface User {
  id: string;
  email: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: User;
}

export interface ResumeSummary {
  id: string;
  title: string;
  created_at: string;
  chunk_count: number;
}

export interface ResumeChunk {
  id: string;
  ordinal: number;
  content: string;
}

export interface ResumeDetail {
  id: string;
  title: string;
  created_at: string;
  raw_text: string;
  chunks: ResumeChunk[];
}

export interface ResumePreviewChunk {
  ordinal: number;
  content: string;
  estimated_tokens: number;
}

export interface ResumePreview {
  chunk_count: number;
  chunks: ResumePreviewChunk[];
}

export type ExtractionStatus = "pending" | "done" | "failed";

export interface JobSummary {
  id: string;
  title: string;
  company: string | null;
  created_at: string;
  extraction_status: ExtractionStatus;
}

export type Seniority = "intern" | "junior" | "mid" | "senior" | "lead" | "unspecified";

export type WorkModel = "remote" | "hybrid" | "onsite" | "unspecified";

export type RequirementKind = "required" | "nice_to_have";

export interface JobRequirement {
  id: string;
  text: string;
  kind: RequirementKind;
}

export interface JobExtraction {
  title: string | null;
  company: string | null;
  seniority: Seniority;
  work_model: WorkModel;
  location: string | null;
  stack: string[];
  requirements: JobRequirement[];
  model: string;
  prompt_version: string;
}

export interface JobDetail extends JobSummary {
  raw_text: string;
  extracted: JobExtraction | null;
}

export type AnalysisStatus = "pending" | "running" | "done" | "failed";

export type Verdict = "met" | "partial" | "not_met";

export interface Evidence {
  chunk_id: string;
  quote: string;
}

export interface RequirementResult {
  id: string;
  text: string;
  kind: RequirementKind;
  verdict: Verdict;
  evidence: Evidence[];
  rationale: string;
}

export interface Gap {
  requirement_id: string;
  text: string;
  kind: RequirementKind;
  verdict: Exclude<Verdict, "met">;
}

export interface Suggestion {
  chunk_id: string;
  original: string;
  suggestion: string;
}

export interface AnalysisResult {
  score: number;
  /** Fração de 0 a 1 por grupo; `null` quando a vaga não tem requisitos daquele tipo. */
  breakdown: { required: number | null; nice_to_have: number | null };
  job: { title: string | null; seniority: Seniority; work_model: WorkModel; stack: string[] };
  requirements: RequirementResult[];
  gaps: Gap[];
  suggestions: Suggestion[];
  model: string;
  prompt_version: string;
}

export interface AnalysisSummary {
  id: string;
  resume_id: string;
  job_id: string;
  status: AnalysisStatus;
  score: number | null;
  error: string | null;
  created_at: string;
  finished_at: string | null;
}

export interface AnalysisCreated extends AnalysisSummary {
  reused: boolean;
}

export interface AnalysisDetail extends AnalysisSummary {
  result: AnalysisResult | null;
}

export interface ScreeningAnswer {
  id: string;
  analysis_id: string;
  question: string;
  answer: string;
  evidence: Evidence[];
  evidence_chunk_ids: string[];
  needs_user_input: boolean;
  user_question: string | null;
  created_at: string;
}

export const APPLICATION_STATUSES = [
  "sent",
  "in_review",
  "tech_test",
  "interview",
  "offer",
  "rejected",
  "no_response",
] as const;

export type ApplicationStatus = (typeof APPLICATION_STATUSES)[number];

export interface Application {
  id: string;
  job: { id: string; title: string; company: string | null };
  analysis_id: string | null;
  platform: string | null;
  status: ApplicationStatus;
  salary_expectation: number | null;
  next_step: string | null;
  /** Data simples `YYYY-MM-DD`, sem fuso. */
  applied_at: string;
  created_at: string;
  updated_at: string;
}
