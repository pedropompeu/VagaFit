import type { ReactNode } from "react";

import { Card } from "./Card";

interface EmptyStateProps {
  title: string;
  description: string;
  action?: ReactNode;
}

export function EmptyState({ title, description, action }: EmptyStateProps) {
  return (
    <Card className="flex flex-col items-center gap-sm px-lg py-2xl text-center">
      <h2 className="text-lg font-semibold text-ink">{title}</h2>
      <p className="max-w-md text-sm text-muted">{description}</p>
      {action ? <div className="mt-xs">{action}</div> : null}
    </Card>
  );
}
