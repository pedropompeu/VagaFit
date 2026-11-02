import type { ReactNode } from "react";

import { Logo } from "../brand/Logo";

interface AuthShellProps {
  title: string;
  description: string;
  children: ReactNode;
}

export function AuthShell({ title, description, children }: AuthShellProps) {
  return (
    <div className="grid min-h-screen bg-canvas lg:grid-cols-2">
      <aside className="hidden flex-col justify-between bg-brand p-2xl text-brand-contrast lg:flex">
        <Logo tone="inverse" className="text-[22px]" />
        <div className="max-w-sm">
          <p className="text-3xl font-semibold leading-tight">Cada ponto, com prova.</p>
          <p className="mt-md text-sm leading-relaxed text-brand-contrast-muted">
            Compare a vaga com o currículo, requisito por requisito. O que não tem prova vira lacuna.
          </p>
        </div>
        <p className="text-xs text-brand-contrast-muted">
          Seus currículos ficam vinculados apenas à sua conta.
        </p>
      </aside>

      <main id="conteudo" className="flex items-center justify-center px-gutter py-2xl">
        <div className="w-full max-w-md">
          <Logo className="mb-xl text-[22px] text-ink lg:hidden" />
          <h1 className="text-2xl font-semibold tracking-tight text-ink">{title}</h1>
          <p className="mt-xs text-sm text-muted">{description}</p>
          <div className="mt-lg">{children}</div>
        </div>
      </main>
    </div>
  );
}
