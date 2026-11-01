import type { ButtonHTMLAttributes } from "react";

import { cn } from "../../lib/cn";
import { Spinner } from "./Spinner";

export type ButtonVariant = "primary" | "secondary" | "danger" | "dangerGhost" | "ghost";
export type ButtonSize = "sm" | "md";

const variantClasses: Record<ButtonVariant, string> = {
  primary: "bg-brand text-brand-contrast hover:bg-brand-hover",
  secondary: "border border-line bg-surface text-ink hover:border-brand hover:text-brand",
  danger: "bg-danger text-danger-contrast hover:bg-danger-hover",
  dangerGhost: "text-danger hover:bg-danger-soft",
  ghost: "text-muted hover:bg-brand-soft hover:text-brand",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "px-sm py-2xs text-sm",
  md: "px-md py-sm text-sm",
};

export function buttonClasses(
  variant: ButtonVariant = "primary",
  size: ButtonSize = "md",
  className?: string,
): string {
  return cn(
    "inline-flex items-center justify-center gap-xs rounded-md font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-60",
    variantClasses[variant],
    sizeClasses[size],
    className,
  );
}

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
}

export function Button({
  variant = "primary",
  size = "md",
  isLoading = false,
  disabled,
  className,
  children,
  type = "button",
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={buttonClasses(variant, size, className)}
      disabled={disabled ?? isLoading}
      aria-busy={isLoading || undefined}
      {...props}
    >
      {isLoading ? <Spinner className="h-4 w-4" label="" /> : null}
      {children}
    </button>
  );
}
