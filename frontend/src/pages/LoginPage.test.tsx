import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { AxiosError, AxiosHeaders, type AxiosResponse } from "axios";
import { MemoryRouter, Route, Routes } from "react-router-dom";

import { ROUTER_FUTURE } from "../test/router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { LoginPage } from "./LoginPage";

const login = vi.fn<(email: string, password: string) => Promise<void>>();
let sessionExpired = false;
vi.mock("../auth/AuthContext", () => ({ useAuth: () => ({ login, sessionExpired }) }));

function renderLogin(state?: unknown) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: "/entrar", state }]} future={ROUTER_FUTURE}>
      <Routes>
        <Route path="/entrar" element={<LoginPage />} />
        <Route path="/curriculos" element={<p>tela de currículos</p>} />
        <Route path="/vagas" element={<p>tela de vagas</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

async function fillAndSubmit(email: string, password: string) {
  const user = userEvent.setup();
  await user.type(screen.getByLabelText(/E-mail/), email);
  await user.type(screen.getByLabelText(/Senha/), password);
  await user.click(screen.getByRole("button", { name: "Entrar" }));
}

describe("LoginPage", () => {
  beforeEach(() => {
    login.mockReset();
    sessionExpired = false;
  });

  it("entra com o e-mail sem espaços e vai para os currículos", async () => {
    login.mockResolvedValue(undefined);
    renderLogin();

    await fillAndSubmit("  ana@vagafit.example ", "segredo-123");

    expect(login).toHaveBeenCalledWith("ana@vagafit.example", "segredo-123");
    expect(await screen.findByText("tela de currículos")).toBeTruthy();
  });

  it("volta para a página que pediu o login", async () => {
    login.mockResolvedValue(undefined);
    renderLogin({ from: { pathname: "/vagas", search: "", hash: "" } });

    await fillAndSubmit("ana@vagafit.example", "segredo-123");

    expect(await screen.findByText("tela de vagas")).toBeTruthy();
  });

  it("mostra o erro da API e continua na tela", async () => {
    const response = {
      status: 401,
      statusText: "",
      headers: {},
      config: { headers: new AxiosHeaders() },
      data: { error: { code: "invalid_credentials", message: "E-mail ou senha incorretos." } },
    } as AxiosResponse;
    login.mockRejectedValue(new AxiosError("401", "ERR_BAD_REQUEST", undefined, undefined, response));
    renderLogin();

    await fillAndSubmit("ana@vagafit.example", "errada");

    expect(await screen.findByText("E-mail ou senha incorretos.")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Entrar" })).toBeTruthy();
  });

  it("explica que a sessão expirou quando ela caiu sozinha", () => {
    sessionExpired = true;
    renderLogin();
    expect(screen.getByText("Sua sessão expirou. Entre de novo para continuar.")).toBeTruthy();
  });

  it("não fala de sessão expirada num acesso normal", () => {
    renderLogin();
    expect(screen.queryByText(/sessão expirou/)).toBeNull();
  });

  it("mostra o aviso que veio de outra tela", () => {
    renderLogin({ notice: "Conta apagada." });
    expect(screen.getByText("Conta apagada.")).toBeTruthy();
  });
});
