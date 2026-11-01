import { cn } from "../../lib/cn";

interface SpinnerProps {
  className?: string;
  label?: string;
}

export function Spinner({ className, label = "Carregando…" }: SpinnerProps) {
  return (
    <span
      role={label ? "status" : undefined}
      aria-hidden={label ? undefined : true}
      className="inline-flex items-center"
    >
      <span
        aria-hidden="true"
        className={cn(
          "animate-spin rounded-full border-2 border-current border-r-transparent",
          className ?? "h-5 w-5",
        )}
      />
      {label ? <span className="sr-only">{label}</span> : null}
    </span>
  );
}
