import { render, screen } from "@testing-library/react";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";

import { ROUTER_FUTURE } from "../test/router";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { AuthStatus } from "./AuthContext";
import { PublicOnly, RequireAuth } from "./guards";

let status: AuthStatus = "anonymous";
vi.mock("./AuthContext", () => ({ useAuth: () => ({ status }) }));

function LoginProbe() {
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } } | null)?.from?.pathname;
  return <p>login (voltar para {from ?? "nada"})</p>;
}

function renderAt(path: string, state?: unknown) {
  return render(
    <MemoryRouter initialEntries={[{ pathname: path, state }]} future={ROUTER_FUTURE}>
      <Routes>
        <Route element={<RequireAuth />}>
          <Route path="/vagas" element={<p>área logada</p>} />
        </Route>
        <Route element={<PublicOnly />}>
          <Route path="/entrar" element={<LoginProbe />} />
        </Route>
        <Route path="/curriculos" element={<p>currículos</p>} />
      </Routes>
    </MemoryRouter>,
  );
}

describe("RequireAuth", () => {
  beforeEach(() => {
    status = "anonymous";
  });

  it("manda para o login lembrando de onde veio", () => {
    renderAt("/vagas");
    expect(screen.getByText("login (voltar para /vagas)")).toBeTruthy();
  });

  it("mostra a página com sessão ativa", () => {
    status = "authenticated";
    renderAt("/vagas");
    expect(screen.getByText("área logada")).toBeTruthy();
  });

  it("espera a sessão ser restaurada antes de decidir", () => {
    status = "loading";
    renderAt("/vagas");
    expect(screen.queryByText("área logada")).toBeNull();
    expect(screen.queryByText(/login/)).toBeNull();
  });
});

describe("PublicOnly", () => {
  it("tira quem já está logado da tela de login", () => {
    status = "authenticated";
    renderAt("/entrar");
    expect(screen.getByText("currículos")).toBeTruthy();
  });

  it("deixa o aviso de conta apagada aparecer no login", () => {
    status = "authenticated";
    renderAt("/entrar", { notice: "Conta apagada." });
    expect(screen.getByText(/^login/)).toBeTruthy();
  });
});
