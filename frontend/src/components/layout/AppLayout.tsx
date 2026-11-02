import {
  BriefcaseIcon,
  Cog6ToothIcon,
  DocumentMagnifyingGlassIcon,
  DocumentTextIcon,
  ViewColumnsIcon,
} from "@heroicons/react/24/outline";
import { useState, type ComponentType, type SVGProps } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";

import { useAuth } from "../../auth/AuthContext";
import { cn } from "../../lib/cn";
import { Logo } from "../brand/Logo";
import { Button } from "../ui/Button";

function navLinkClass({ isActive }: { isActive: boolean }): string {
  return cn(
    "inline-flex items-center gap-2xs rounded-md px-xs py-2xs text-sm font-medium transition-colors",
    // Página atual não depende só de cor: sublinhado de 2px além do fundo (BRAND.md 8.10).
    isActive
      ? "bg-brand-soft text-brand underline decoration-2 underline-offset-[6px]"
      : "text-muted hover:bg-brand-soft hover:text-brand",
  );
}

const NAV: { to: string; label: string; Icon: ComponentType<SVGProps<SVGSVGElement>> }[] = [
  { to: "/curriculos", label: "Currículos", Icon: DocumentTextIcon },
  { to: "/vagas", label: "Vagas", Icon: BriefcaseIcon },
  { to: "/analises", label: "Análises", Icon: DocumentMagnifyingGlassIcon },
  { to: "/candidaturas", label: "Candidaturas", Icon: ViewColumnsIcon },
  { to: "/configuracoes", label: "Configurações", Icon: Cog6ToothIcon },
];

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
            <Logo className="text-[19px] text-ink" />
            <nav aria-label="Navegação principal" className="flex flex-wrap items-center gap-2xs">
              {NAV.map(({ to, label, Icon }) => (
                <NavLink key={to} to={to} className={navLinkClass}>
                  <Icon className="size-4" aria-hidden="true" />
                  {label}
                </NavLink>
              ))}
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
          VagaFit · aderência entre vaga e currículo, com evidência
        </div>
      </footer>
    </div>
  );
}
