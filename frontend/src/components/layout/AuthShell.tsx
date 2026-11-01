import type { ReactNode } from "react";

interface AuthShellProps {
  title: string;
  description: string;
  children: ReactNode;
}

export function AuthShell({ title, description, children }: AuthShellProps) {
  return (
    <div className="grid min-h-screen bg-canvas lg:grid-cols-2">
      <aside className="hidden flex-col justify-between bg-brand p-2xl text-brand-contrast lg:flex">
        <span className="text-xl font-semibold tracking-tight">VagaFit</span>
        <div className="max-w-sm">
          <p className="text-3xl font-semibold leading-tight">
            Currículos e vagas organizados no mesmo lugar.
          </p>
          <p className="mt-md text-sm leading-relaxed text-brand-contrast-muted">
            Guarde seus currículos, cadastre vagas e acompanhe os requisitos extraídos de cada
            oportunidade.
          </p>
        </div>
        <p className="text-xs text-brand-contrast-muted">
          Seus currículos ficam vinculados apenas à sua conta.
        </p>
      </aside>

      <main id="conteudo" className="flex items-center justify-center px-gutter py-2xl">
        <div className="w-full max-w-md">
          <p className="mb-xl text-xl font-semibold tracking-tight text-brand lg:hidden">VagaFit</p>
          <h1 className="text-2xl font-semibold tracking-tight text-ink">{title}</h1>
          <p className="mt-xs text-sm text-muted">{description}</p>
          <div className="mt-lg">{children}</div>
        </div>
      </main>
    </div>
  );
}
