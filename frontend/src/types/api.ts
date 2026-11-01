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

export type ExtractionStatus = "pending" | "done";

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
