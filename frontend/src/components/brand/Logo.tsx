import { useId } from "react";

import { cn } from "../../lib/cn";

/*
 * Logo do VagaFit (BRAND.md, seção 02): símbolo "Infinito com duas pessoas" (1a, desenho da rodada 3)
 * e wordmark "vagafit" em Plex Mono 500 com o "fit" grifado.
 * A geometria é a mesma de brand/logo/*.svg. Não editar sem atualizar os SVGs e o BRAND.md juntos.
 */
const INFINITY =
  "M26.2 26.6C20.6 20 11.2 20 11.2 26.6C11.2 33.2 20.6 33.2 26.2 26.6C31.8 20 41.4 20 41.4 26.6C41.4 33.2 31.8 33.2 26.2 26.6Z";
const OVER = "M19.69 31.04C21.95 30.33 24.3 28.84 26.2 26.6C28.1 24.36 30.47 22.87 32.76 22.16";
const ARC = "M37.05 11.33A19.6 19.6 0 1 0 28.3 41.82A19.05 19.05 0 1 1 37.05 11.33Z";

type LogoTone = "default" | "inverse";

/**
 * Cores das duas figuras. "inverse" é para o fundo da ação (bg-brand, como a lateral do login):
 * usa os tokens de texto sobre a ação, que se invertem sozinhos no modo escuro.
 */
const SYMBOL_COLORS: Record<LogoTone, { you: string; job: string }> = {
  default: { you: "var(--color-logo-you)", job: "var(--color-logo-job)" },
  inverse: { you: "var(--color-brand-contrast)", job: "var(--color-brand-contrast-muted)" },
};

interface LogoMarkProps {
  tone?: LogoTone;
  className?: string;
  /** Sem título, o símbolo é decorativo (o nome já está ao lado). */
  title?: string;
}

export function LogoMark({ tone = "default", className, title }: LogoMarkProps) {
  // useId gera ":r0:"; os dois-pontos atrapalham em url(#...).
  const id = `vf${useId().replace(/:/g, "")}`;
  const { you, job } = SYMBOL_COLORS[tone];
  const a11y = title ? { role: "img", "aria-label": title } : { "aria-hidden": true, focusable: false };

  return (
    <svg viewBox="0 0 48 48" className={cn("shrink-0", className)} {...a11y}>
      <defs>
        <linearGradient id={`${id}-g`} gradientUnits="userSpaceOnUse" x1="21.2" y1="0" x2="31.2" y2="0">
          <stop offset="0" stopColor={you} />
          <stop offset="1" stopColor={job} />
        </linearGradient>
        <mask id={`${id}-m`} maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48">
          <rect width="48" height="48" fill="#fff" />
          <path d={OVER} fill="none" stroke="#000" strokeWidth="7.4" />
        </mask>
      </defs>
      <path d={ARC} fill={job} />
      <path
        d={INFINITY}
        fill="none"
        stroke={`url(#${id}-g)`}
        strokeWidth="5.2"
        strokeLinejoin="round"
        mask={`url(#${id}-m)`}
      />
      <path d={OVER} fill="none" stroke={`url(#${id}-g)`} strokeWidth="5.2" />
      <circle cx="18.6" cy="14.2" r="3.5" fill={you} />
      <circle cx="35" cy="14.2" r="3.5" fill={job} />
    </svg>
  );
}

interface LogoProps {
  tone?: LogoTone;
  className?: string;
}

/**
 * Lockup: símbolo com ~1,5 vez o corpo do texto e respiro de 0,4 corpo (proporção da prancha).
 * O tamanho vem do font-size do contêiner (ex.: `text-[19px]`).
 * No tom "inverse" o grifo vira sublinhado, como na variante mono: texto claro sobre âmbar não lê.
 */
export function Logo({ tone = "default", className }: LogoProps) {
  return (
    <span className={cn("inline-flex items-center gap-[0.4em] leading-none", className)}>
      <LogoMark tone={tone} className="h-[1.5em] w-[1.5em]" />
      <span className="whitespace-nowrap font-mono font-medium tracking-[-0.01em]">
        <span className="sr-only">VagaFit</span>
        <span aria-hidden="true">
          vaga
          <span
            className={cn(
              "px-[0.04em]",
              tone === "default"
                ? "bg-[linear-gradient(transparent_56%,var(--color-logo-grifo)_56%)]"
                : "underline decoration-2 underline-offset-[0.18em]",
            )}
          >
            fit
          </span>
        </span>
      </span>
    </span>
  );
}
