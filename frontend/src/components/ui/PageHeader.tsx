import { ArrowLeftIcon } from "@heroicons/react/24/outline";
import type { ReactNode } from "react";
import { Link } from "react-router-dom";

interface PageHeaderProps {
  title: string;
  description?: string;
  actions?: ReactNode;
  backTo?: string;
  backLabel?: string;
}

export function PageHeader({
  title,
  description,
  actions,
  backTo,
  backLabel = "Voltar",
}: PageHeaderProps) {
  return (
    <div className="mb-lg flex flex-col gap-sm sm:flex-row sm:items-start sm:justify-between">
      <div className="min-w-0">
        {backTo ? (
          <Link
            to={backTo}
            className="mb-2xs inline-flex items-center gap-2xs text-sm text-muted transition-colors hover:text-brand"
          >
            <ArrowLeftIcon className="size-4" aria-hidden="true" />
            {backLabel}
          </Link>
        ) : null}
        <h1 className="text-2xl font-semibold tracking-tight text-ink">{title}</h1>
        {description ? <p className="mt-2xs max-w-2xl text-sm text-muted">{description}</p> : null}
      </div>
      {actions ? <div className="flex flex-wrap items-center gap-xs">{actions}</div> : null}
    </div>
  );
}
