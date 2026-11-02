import { ChevronDownIcon } from "@heroicons/react/24/outline";
import type { ReactNode } from "react";

import { cn } from "../../lib/cn";

interface DisclosureProps {
  summary: ReactNode;
  children: ReactNode;
  /** "brand" para links de evidência; "ink" para blocos de texto bruto. */
  tone?: "brand" | "ink";
  className?: string;
}

/** `<details>` com chevron Heroicons no lugar do triângulo nativo (BRAND.md 7). */
export function Disclosure({ summary, children, tone = "brand", className }: DisclosureProps) {
  return (
    <details className={cn("group", className)}>
      <summary
        className={cn(
          "inline-flex cursor-pointer list-none items-center gap-2xs rounded-sm text-sm font-medium transition-colors hover:underline [&::-webkit-details-marker]:hidden",
          tone === "brand"
            ? "text-brand hover:text-brand-hover active:text-brand-active"
            : "text-ink",
        )}
      >
        {summary}
        <ChevronDownIcon
          className="size-4 transition-transform duration-base group-open:rotate-180"
          aria-hidden="true"
        />
      </summary>
      {children}
    </details>
  );
}
