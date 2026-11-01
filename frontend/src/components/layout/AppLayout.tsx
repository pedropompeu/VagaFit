import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../../auth/AuthContext";
import { cn } from "../../lib/cn";
import { Button } from "../ui/Button";

function navLinkClass({ isActive }: { isActive: boolean }): string {
  return cn(
    "rounded-md px-xs py-2xs text-sm font-medium transition-colors",
    isActive ? "bg-brand-soft text-brand" : "text-muted hover:bg-brand-soft hover:text-brand",
  );
}

export function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  async function handleLogout() {
    if (isLoggingOut) return;
    setIsLoggingOut(true);
    try {
      await logout();
      navigate("/entrar", { replace: true });
    } finally {
      setIsLoggingOut(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col">
      <a
        href="#conteudo"
        className="sr-only focus:not-sr-only focus:absolute focus:left-md focus:top-md focus:z-50 focus:rounded-md focus:border focus:border-line focus:bg-surface focus:px-sm focus:py-xs focus:text-sm focus:text-brand"
      >
        Pular para o conteúdo
      </a>

      <header className="border-b border-line bg-surface">
        <div className="mx-auto flex w-full max-w-5xl flex-col gap-sm px-gutter py-sm lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap items-center gap-md">
            <span className="text-lg font-semibold tracking-tight text-brand">VagaFit</span>
            <nav aria-label="Navegação principal" className="flex flex-wrap items-center gap-2xs">
              <NavLink to="/curriculos" className={navLinkClass}>
                Currículos
              </NavLink>
              <NavLink to="/vagas" className={navLinkClass}>
                Vagas
              </NavLink>
              <NavLink to="/analises" className={navLinkClass}>
                Análises
              </NavLink>
              <NavLink to="/candidaturas" className={navLinkClass}>
                Candidaturas
              </NavLink>
              <NavLink to="/configuracoes" className={navLinkClass}>
                Configurações
              </NavLink>
            </nav>
          </div>

          <div className="flex items-center justify-between gap-sm lg:justify-end">
            <span className="min-w-0 truncate text-sm text-muted" title={user?.email}>
              {user?.email}
            </span>
            <Button
              variant="secondary"
              size="sm"
              onClick={() => void handleLogout()}
              isLoading={isLoggingOut}
            >
              Sair
            </Button>
          </div>
        </div>
      </header>

      <main id="conteudo" className="mx-auto w-full max-w-5xl flex-1 px-gutter py-section">
        <Outlet />
      </main>

      <footer className="border-t border-line bg-surface">
        <div className="mx-auto w-full max-w-5xl px-gutter py-md text-xs text-muted">
          VagaFit · preparação para candidaturas com mais contexto
        </div>
      </footer>
    </div>
  );
}
