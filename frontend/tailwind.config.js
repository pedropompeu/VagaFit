/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        canvas: "var(--color-canvas)",
        surface: "var(--color-surface)",
        ink: "var(--color-ink)",
        muted: "var(--color-muted)",
        line: "var(--color-line)",
        overlay: "var(--color-overlay)",
        brand: {
          DEFAULT: "var(--color-brand)",
          hover: "var(--color-brand-hover)",
          contrast: "var(--color-brand-contrast)",
          "contrast-muted": "var(--color-brand-contrast-muted)",
          soft: "var(--color-brand-soft)",
        },
        danger: {
          DEFAULT: "var(--color-danger)",
          hover: "var(--color-danger-hover)",
          contrast: "var(--color-danger-contrast)",
          soft: "var(--color-danger-soft)",
        },
        success: {
          DEFAULT: "var(--color-success)",
          soft: "var(--color-success-soft)",
        },
        warning: {
          DEFAULT: "var(--color-warning)",
          soft: "var(--color-warning-soft)",
        },
      },
      borderRadius: {
        sm: "var(--radius-sm)",
        md: "var(--radius-md)",
        lg: "var(--radius-lg)",
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
      },
      boxShadow: {
        card: "var(--shadow-card)",
      },
    },
  },
  plugins: [],
};
