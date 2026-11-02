import { forwardRef, type InputHTMLAttributes } from "react";

import { cn } from "../../lib/cn";

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  invalid?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { className, invalid = false, ...props },
  ref,
) {
  return (
    <input
      ref={ref}
      aria-invalid={invalid || undefined}
      className={cn(
        "w-full rounded-md border border-line-strong bg-surface px-sm py-xs text-sm text-ink transition-colors",
        "placeholder:text-muted focus:border-brand disabled:cursor-not-allowed disabled:bg-canvas",
        invalid && "border-danger",
        className,
      )}
      {...props}
    />
  );
});
