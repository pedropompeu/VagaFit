import axios, { type InternalAxiosRequestConfig } from "axios";

import type { AuthResponse } from "../types/api";

const rawBaseUrl = import.meta.env.VITE_API_URL?.trim() || "http://localhost:8000";

/** Base da API, sempre com o prefixo de versão. */
export const API_BASE_URL = `${rawBaseUrl.replace(/\/+$/, "")}/api/v1`;

let accessToken: string | null = null;
let sessionExpiredHandler: (() => void) | null = null;
let refreshPromise: Promise<AuthResponse> | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string | null): void {
  accessToken = token;
}

export function setSessionExpiredHandler(handler: (() => void) | null): void {
  sessionExpiredHandler = handler;
}

// Cliente separado para o refresh: não passa pelo interceptor e evita laço de 401.
const refreshClient = axios.create({ baseURL: API_BASE_URL, withCredentials: true });

/**
 * Renova o access token uma única vez, mesmo com várias requisições concorrentes.
 * O refresh token vive só no cookie httpOnly.
 */
export function refreshSession(): Promise<AuthResponse> {
  if (!refreshPromise) {
    refreshPromise = refreshClient
      .post<AuthResponse>("/auth/refresh")
      .then(({ data }) => {
        setAccessToken(data.access_token);
        return data;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

function notifySessionExpired(): void {
  setAccessToken(null);
  sessionExpiredHandler?.();
}

export const api = axios.create({ baseURL: API_BASE_URL, withCredentials: true });

api.interceptors.request.use((config) => {
  if (accessToken) config.headers.set("Authorization", `Bearer ${accessToken}`);
  return config;
});

interface RetriableRequestConfig extends InternalAxiosRequestConfig {
  _retry?: boolean;
}

// Endpoints de sessão não devem tentar renovar o token depois de um 401.
function shouldSkipRefresh(url: string | undefined): boolean {
  return (
    url === "/auth/login" ||
    url === "/auth/register" ||
    url === "/auth/refresh" ||
    url === "/auth/logout"
  );
}

api.interceptors.response.use(undefined, async (error: unknown) => {
  if (!axios.isAxiosError(error)) return Promise.reject(error);

  const original = error.config as RetriableRequestConfig | undefined;
  const status = error.response?.status;

  if (status !== 401 || !original || original._retry || shouldSkipRefresh(original.url)) {
    return Promise.reject(error);
  }

  original._retry = true;

  try {
    const session = await refreshSession();
    original.headers.set("Authorization", `Bearer ${session.access_token}`);
    return await api.request(original);
  } catch (refreshError) {
    notifySessionExpired();
    return Promise.reject(refreshError);
  }
});
