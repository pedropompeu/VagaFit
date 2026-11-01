import { forwardRef, type SelectHTMLAttributes } from "react";

import { cn } from "../../lib/cn";

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  invalid?: boolean;
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { className, invalid = false, ...props },
  ref,
) {
  return (
    <select
      ref={ref}
      aria-invalid={invalid || undefined}
      className={cn(
        "w-full rounded-md border border-line bg-surface px-sm py-xs text-sm text-ink transition-colors",
        "focus:border-brand disabled:cursor-not-allowed disabled:bg-canvas",
        invalid && "border-danger",
        className,
      )}
      {...props}
    />
  );
});
