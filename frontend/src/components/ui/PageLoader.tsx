import { cn } from "../../lib/cn";
import { Spinner } from "./Spinner";

interface PageLoaderProps {
  label?: string;
  fullScreen?: boolean;
  className?: string;
}

export function PageLoader({
  label = "Carregando…",
  fullScreen = false,
  className,
}: PageLoaderProps) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-sm text-muted",
        fullScreen ? "min-h-screen" : "py-2xl",
        className,
      )}
    >
      <Spinner className="h-8 w-8 text-brand" label={label} />
      <p className="text-sm" aria-hidden="true">
        {label}
      </p>
    </div>
  );
}
