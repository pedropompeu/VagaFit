import {
  CheckCircleIcon,
  ExclamationCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
} from "@heroicons/react/24/outline";
import type { ComponentType, ReactNode, SVGProps } from "react";

import { cn } from "../../lib/cn";

export type AlertVariant = "error" | "success" | "info" | "warning";

const variantClasses: Record<AlertVariant, string> = {
  error: "border-danger bg-danger-soft text-danger",
  success: "border-success bg-success-soft text-success",
  info: "border-brand bg-brand-soft text-brand",
  warning: "border-warning bg-warning-soft text-warning",
};

/** Status nunca só por cor: cada variante tem o seu ícone (BRAND.md 8.8). */
const variantIcons: Record<AlertVariant, ComponentType<SVGProps<SVGSVGElement>>> = {
  error: ExclamationCircleIcon,
  success: CheckCircleIcon,
  info: InformationCircleIcon,
  warning: ExclamationTriangleIcon,
};

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  className?: string;
  children?: ReactNode;
}

export function Alert({ variant = "info", title, className, children }: AlertProps) {
  const Icon = variantIcons[variant];
  return (
    <div
      role={variant === "error" ? "alert" : "status"}
      className={cn("flex gap-xs rounded-md border px-md py-sm text-sm", variantClasses[variant], className)}
    >
      <Icon className="mt-px size-5 shrink-0" aria-hidden="true" />
      <div className="min-w-0 flex-1">
        {title ? <p className="font-medium">{title}</p> : null}
        {children ? <div className={cn(title && "mt-2xs")}>{children}</div> : null}
      </div>
    </div>
  );
}
