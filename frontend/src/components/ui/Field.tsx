import type { ReactNode } from "react";

interface FieldProps {
  label: string;
  htmlFor: string;
  hint?: ReactNode;
  error?: string | null;
  required?: boolean;
  children: ReactNode;
}

export function Field({ label, htmlFor, hint, error, required = false, children }: FieldProps) {
  const hintId = `${htmlFor}-hint`;
  const errorId = `${htmlFor}-error`;

  return (
    <div className="flex flex-col gap-2xs">
      <label htmlFor={htmlFor} className="text-sm font-medium text-ink">
        {label}
        {required ? (
          <span className="text-danger" aria-hidden="true">
            {" "}
            *
          </span>
        ) : null}
      </label>
      {children}
      {error ? (
        <p id={errorId} role="alert" className="text-xs text-danger">
          {error}
        </p>
      ) : hint ? (
        <p id={hintId} className="text-xs text-muted">
          {hint}
        </p>
      ) : null}
    </div>
  );
}
