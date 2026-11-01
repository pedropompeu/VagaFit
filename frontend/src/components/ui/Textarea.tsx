import { forwardRef, type TextareaHTMLAttributes } from "react";

import { cn } from "../../lib/cn";

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  invalid?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { className, invalid = false, rows = 10, ...props },
  ref,
) {
  return (
    <textarea
      ref={ref}
      rows={rows}
      aria-invalid={invalid || undefined}
      className={cn(
        "w-full resize-y rounded-md border border-line bg-surface px-sm py-xs text-sm text-ink transition-colors",
        "placeholder:text-muted focus:border-brand disabled:cursor-not-allowed disabled:bg-canvas",
        invalid && "border-danger",
        className,
      )}
      {...props}
    />
  );
});
