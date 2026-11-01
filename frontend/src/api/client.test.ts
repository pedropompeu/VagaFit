import axios, { AxiosError, type AxiosAdapter, type InternalAxiosRequestConfig } from "axios";
import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";

type ClientModule = typeof import("./client");

// Servidor de mentira: responde pela URL e registra cada chamada.
const calls: { url: string; auth: string | null }[] = [];
let validToken = "novo";
let refreshFails = false;

function reply(config: InternalAxiosRequestConfig, status: number, data: unknown) {
  const response = { status, statusText: "", headers: {}, config, data };
  if (status >= 400) {
    return Promise.reject(
      new AxiosError(`status ${status}`, "ERR_BAD_RESPONSE", config, undefined, response),
    );
  }
  return Promise.resolve(response);
}

const adapter: AxiosAdapter = (config) => {
  const url = config.url ?? "";
  const auth = config.headers.get("Authorization");
  calls.push({ url, auth: typeof auth === "string" ? auth : null });
  if (url === "/auth/refresh") {
    if (refreshFails) return reply(config, 401, {});
    return reply(config, 200, { access_token: validToken, user: { id: "u1" } });
  }
  if (auth === `Bearer ${validToken}`) return reply(config, 200, { ok: url });
  return reply(config, 401, {});
};

let client: ClientModule;

beforeAll(async () => {
  // Os clientes copiam o adapter padrão ao serem criados, então ele vem antes do import.
  axios.defaults.adapter = adapter;
  client = await import("./client");
});

beforeEach(() => {
  calls.length = 0;
  validToken = "novo";
  refreshFails = false;
  client.setAccessToken("vencido");
  client.setSessionExpiredHandler(null);
});

describe("cliente da API", () => {
  it("manda o token e usa o prefixo de versão", () => {
    expect(client.API_BASE_URL.endsWith("/api/v1")).toBe(true);
  });

  it("renova o token num 401 e repete o pedido", async () => {
    const { data } = await client.api.get("/jobs");

    expect(data).toEqual({ ok: "/jobs" });
    expect(calls.map((c) => c.url)).toEqual(["/jobs", "/auth/refresh", "/jobs"]);
    expect(calls[0]?.auth).toBe("Bearer vencido");
    expect(calls[2]?.auth).toBe("Bearer novo");
    expect(client.getAccessToken()).toBe("novo");
  });

  it("faz um refresh só para vários 401 ao mesmo tempo", async () => {
    await Promise.all([client.api.get("/jobs"), client.api.get("/resumes")]);

    expect(calls.filter((c) => c.url === "/auth/refresh")).toHaveLength(1);
  });

  it("encerra a sessão quando o refresh falha", async () => {
    refreshFails = true;
    const expired = vi.fn();
    client.setSessionExpiredHandler(expired);

    await expect(client.api.get("/jobs")).rejects.toBeInstanceOf(AxiosError);

    expect(expired).toHaveBeenCalledOnce();
    expect(client.getAccessToken()).toBeNull();
  });

  it("não tenta renovar quando o próprio login dá 401", async () => {
    await expect(client.api.post("/auth/login", {})).rejects.toBeInstanceOf(AxiosError);

    expect(calls.map((c) => c.url)).toEqual(["/auth/login"]);
  });
});
