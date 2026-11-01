import type { AuthResponse, User } from "../types/api";
import { api } from "./client";

export async function loginRequest(email: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/login", { email, password });
  return data;
}

export async function registerRequest(email: string, password: string): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/auth/register", { email, password });
  return data;
}

export async function logoutRequest(): Promise<void> {
  await api.post("/auth/logout");
}

export async function getCurrentUser(): Promise<User> {
  const { data } = await api.get<User>("/auth/me");
  return data;
}

export async function deleteAccountRequest(password: string): Promise<void> {
  await api.delete("/auth/me", { data: { password } });
}
