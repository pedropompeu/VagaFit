/**
 * VagaFit — tailwind.config.ts (MAXWELL, 2026-11-01). Tailwind 3.4.
 * Substitui tailwind.config.js. Toda cor é var(): o tema claro/escuro vive no CSS (design-tokens.css).
 * Chaves legadas preservadas (canvas, surface, ink, muted, line, overlay, brand, danger, success,
 * warning, radius, spacing, font-sans, shadow-card), então os componentes atuais não mudam.
 */
import type { Config } from "tailwindcss";

/** Monta o par [tamanho, { lineHeight, fontWeight, letterSpacing }] a partir dos tokens --text-*. */
const scale = (name: string): [string, { lineHeight: string; fontWeight: string; letterSpacing: string }] => [
  `var(--text-${name}-size)`,
  {
    lineHeight: `var(--text-${name}-lh)`,
    fontWeight: `var(--text-${name}-weight)`,
    letterSpacing: `var(--text-${name}-tracking)`,
  },
];

/** Alias das chaves padrão do Tailwind (text-sm etc.): só tamanho e line-height, para não
 *  forçar peso e não brigar com font-medium/font-semibold já usados nos componentes. */
const alias = (name: string): [string, string] => [`var(--text-${name}-size)`, `var(--text-${name}-lh)`];

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // --- Nomes legados (troca direta) ---
        canvas: "var(--color-canvas)",
        surface: "var(--color-surface)",
        sunken: "var(--color-sunken)", // novo: área rebaixada
        ink: "var(--color-ink)",
        muted: "var(--color-muted)",
        line: {
          DEFAULT: "var(--color-line)",
          strong: "var(--color-line-strong)", // novo: borda de controle (>= 3:1)
        },
        overlay: "var(--color-overlay)",
        brand: {
          DEFAULT: "var(--color-brand)",
          hover: "var(--color-brand-hover)",
          active: "var(--color-brand-active)", // novo
          contrast: "var(--color-brand-contrast)",
          "contrast-muted": "var(--color-brand-contrast-muted)",
          soft: "var(--color-brand-soft)",
        },
        danger: {
          DEFAULT: "var(--color-danger)",
          hover: "var(--color-danger-hover)",
          active: "var(--color-danger-active)", // novo
          contrast: "var(--color-danger-contrast)",
          soft: "var(--color-danger-soft)",
        },
        success: {
          DEFAULT: "var(--color-success)",
          soft: "var(--color-success-soft)",
        },
        // warning = terracota (o âmbar é exclusivo da evidência)
        warning: {
          DEFAULT: "var(--color-warning)",
          soft: "var(--color-warning-soft)",
        },

        // --- Novos: evidência (único uso permitido do âmbar) ---
        evidence: {
          bg: "var(--color-evidence-bg)", // marca-texto
          soft: "var(--color-evidence-bg-soft)", // bloco da citação
          border: "var(--color-evidence-border)",
          text: "var(--color-evidence-text)",
          meta: "var(--color-evidence-meta)", // ID do trecho
        },

        // --- Novos: vereditos (sempre com ícone + texto) ---
        // Uso: text-verdict-met-text bg-verdict-met-bg border-verdict-met-border
        verdict: {
          "met-text": "var(--color-verdict-met-text)",
          "met-bg": "var(--color-verdict-met-bg)",
          "met-border": "var(--color-verdict-met-border)",
          "partial-text": "var(--color-verdict-partial-text)",
          "partial-bg": "var(--color-verdict-partial-bg)",
          "partial-border": "var(--color-verdict-partial-border)",
          "not-met-text": "var(--color-verdict-not-met-text)",
          "not-met-bg": "var(--color-verdict-not-met-bg)",
          "not-met-border": "var(--color-verdict-not-met-border)",
          "no-evidence-text": "var(--color-verdict-no-evidence-text)",
          "no-evidence-bg": "var(--color-verdict-no-evidence-bg)",
          "no-evidence-border": "var(--color-verdict-no-evidence-border)", // usar com border-dashed
        },

        // --- Novos: score (neutro, nunca semáforo) ---
        score: {
          bg: "var(--color-score-bg)",
          text: "var(--color-score-text)",
          border: "var(--color-score-border)",
        },

        // --- Novos: data viz (só petróleo) ---
        dataviz: {
          track: "var(--color-dataviz-track)",
          1: "var(--color-dataviz-fill-1)",
          2: "var(--color-dataviz-fill-2)",
          3: "var(--color-dataviz-fill-3)",
        },

        // --- Logo: as duas figuras do símbolo e o grifo do wordmark (seção 02) ---
        logo: {
          you: "var(--color-logo-you)",
          job: "var(--color-logo-job)",
          grifo: "var(--color-logo-grifo)",
        },

        // --- Novo: foco ---
        focus: "var(--focus-ring-color)",
      },

      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
        full: "var(--radius-full)",
      },

      spacing: {
        "2xs": "var(--space-2xs)",
        xs: "var(--space-xs)",
        sm: "var(--space-sm)",
        md: "var(--space-md)",
        lg: "var(--space-lg)",
        xl: "var(--space-xl)",
        "2xl": "var(--space-2xl)",
        gutter: "var(--space-gutter)",
        section: "var(--space-section)",
      },

      fontFamily: {
        sans: "var(--font-sans)",
        display: "var(--font-display)",
        mono: "var(--font-mono)",
      },

      // Escala tipográfica. Nomes semânticos (text-h1...) levam tamanho + line-height + peso + tracking.
      // As chaves padrão (xs...4xl) viram alias da escala, sem peso, para os componentes atuais.
      fontSize: {
        display: scale("display"),
        h1: scale("h1"),
        h2: scale("h2"),
        h3: scale("h3"),
        h4: scale("h4"),
        body: scale("body"),
        "body-sm": scale("body-sm"),
        label: scale("label"),
        caption: scale("caption"),
        micro: scale("micro"),
        mono: scale("mono"),
        "mono-sm": scale("mono-sm"),
        xs: alias("micro"),
        sm: alias("body-sm"),
        base: alias("body"),
        lg: alias("h4"),
        xl: alias("h3"),
        "2xl": alias("h2"),
        "3xl": alias("h1"),
        "4xl": alias("display"),
      },

      boxShadow: {
        card: "var(--shadow-card)",
        popover: "var(--shadow-popover)", // novo: menus e popovers (não chamar de "overlay": conflitaria com a cor overlay em shadow-*)
        dialog: "var(--shadow-dialog)", // novo: diálogos
      },

      // Foco: o anel usa outline (ver index.css); estes tokens servem a ring-* quando necessário.
      ringColor: { DEFAULT: "var(--focus-ring-color)" },
      ringWidth: { DEFAULT: "var(--focus-ring-width)" },
      ringOffsetWidth: { DEFAULT: "var(--focus-ring-offset)" },

      // Motion: transition-colors etc. passam a respeitar prefers-reduced-motion via variável.
      transitionDuration: {
        DEFAULT: "var(--motion-duration-fast)",
        fast: "var(--motion-duration-fast)",
        base: "var(--motion-duration-base)",
        slow: "var(--motion-duration-slow)",
      },
      transitionTimingFunction: {
        DEFAULT: "var(--motion-ease-standard)",
        standard: "var(--motion-ease-standard)",
        enter: "var(--motion-ease-enter)",
        exit: "var(--motion-ease-exit)",
      },
      animation: {
        // sobrescreve animate-spin: a duração vem do token e fica lenta em reduced motion
        spin: "spin var(--motion-duration-spin) var(--motion-ease-linear) infinite",
      },

      strokeWidth: {
        icon: "var(--icon-stroke-width)", // Heroicons outline, traço 1.5: className="stroke-icon"
      },

      zIndex: {
        sticky: "var(--z-sticky)",
        dropdown: "var(--z-dropdown)",
        overlay: "var(--z-overlay)",
        dialog: "var(--z-dialog)",
        toast: "var(--z-toast)",
      },

      maxWidth: {
        container: "var(--size-container-max)",
        measure: "var(--size-measure)", // leitura longa de citações
      },
    },
  },
  plugins: [],
} satisfies Config;
