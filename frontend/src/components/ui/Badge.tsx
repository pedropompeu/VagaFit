import type { ReactNode } from "react";

import { cn } from "../../lib/cn";

export type BadgeTone = "neutral" | "brand" | "success" | "warning" | "danger";

const toneClasses: Record<BadgeTone, string> = {
  neutral: "bg-canvas text-muted",
  brand: "bg-brand-soft text-brand",
  success: "bg-success-soft text-success",
  warning: "bg-warning-soft text-warning",
  danger: "bg-danger-soft text-danger",
};

interface BadgeProps {
  tone?: BadgeTone;
  className?: string;
  children: ReactNode;
}

export function Badge({ tone = "neutral", className, children }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-2xs rounded-full px-xs py-2xs text-xs font-medium",
        toneClasses[tone],
        className,
      )}
    >
      {children}
    </span>
  );
}
