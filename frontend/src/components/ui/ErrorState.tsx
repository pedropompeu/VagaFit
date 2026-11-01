import { Button } from "./Button";
import { Card } from "./Card";

interface ErrorStateProps {
  title?: string;
  description: string;
  onRetry?: () => void;
  retryLabel?: string;
}

export function ErrorState({
  title = "Não foi possível carregar",
  description,
  onRetry,
  retryLabel = "Tentar novamente",
}: ErrorStateProps) {
  return (
    <Card className="flex flex-col items-center gap-sm px-lg py-2xl text-center">
      <h2 className="text-lg font-semibold text-ink">{title}</h2>
      <p className="max-w-md text-sm text-muted">{description}</p>
      {onRetry ? (
        <Button variant="secondary" onClick={onRetry} className="mt-xs">
          {retryLabel}
        </Button>
      ) : null}
    </Card>
  );
}
