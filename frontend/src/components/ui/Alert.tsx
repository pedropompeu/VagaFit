import type { ReactNode } from "react";

import { cn } from "../../lib/cn";

export type AlertVariant = "error" | "success" | "info" | "warning";

const variantClasses: Record<AlertVariant, string> = {
  error: "border-danger bg-danger-soft text-danger",
  success: "border-success bg-success-soft text-success",
  info: "border-brand bg-brand-soft text-brand",
  warning: "border-warning bg-warning-soft text-warning",
};

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  className?: string;
  children?: ReactNode;
}

export function Alert({ variant = "info", title, className, children }: AlertProps) {
  return (
    <div
      role={variant === "error" ? "alert" : "status"}
      className={cn("rounded-md border px-md py-sm text-sm", variantClasses[variant], className)}
    >
      {title ? <p className="font-medium">{title}</p> : null}
      {children ? <div className={cn(title && "mt-2xs")}>{children}</div> : null}
    </div>
  );
}
