import { useEffect, useId, useRef, type ReactNode, type RefObject } from "react";

import { Button } from "./Button";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description?: ReactNode;
  confirmLabel?: string;
  cancelLabel?: string;
  tone?: "primary" | "danger";
  isConfirming?: boolean;
  confirmDisabled?: boolean;
  initialFocusRef?: RefObject<HTMLElement>;
  onConfirm: () => void;
  onClose: () => void;
  children?: ReactNode;
}

export function ConfirmDialog({
  open,
  title,
  description,
  confirmLabel = "Confirmar",
  cancelLabel = "Cancelar",
  tone = "primary",
  isConfirming = false,
  confirmDisabled = false,
  initialFocusRef,
  onConfirm,
  onClose,
  children,
}: ConfirmDialogProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  const descriptionId = useId();

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;

    if (open) {
      if (!dialog.open) dialog.showModal();
      initialFocusRef?.current?.focus();
    } else if (dialog.open) {
      dialog.close();
    }
  }, [open, initialFocusRef]);

  useEffect(() => {
    if (!open) return;
    const dialog = dialogRef.current;
    if (!dialog) return;

    const handleCancel = (event: Event) => {
      event.preventDefault();
      if (!isConfirming) onClose();
    };

    dialog.addEventListener("cancel", handleCancel);
    return () => {
      dialog.removeEventListener("cancel", handleCancel);
    };
  }, [open, isConfirming, onClose]);

  return (
    <dialog
      ref={dialogRef}
      aria-labelledby={titleId}
      aria-describedby={description ? descriptionId : undefined}
      onClick={(event) => {
        if (event.target === event.currentTarget && !isConfirming) onClose();
      }}
      className="w-[calc(100%-2rem)] max-w-lg rounded-lg border border-line bg-surface p-0 text-ink shadow-card backdrop:bg-overlay"
    >
      <div className="p-lg">
        <h2 id={titleId} className="text-lg font-semibold text-ink">
          {title}
        </h2>
        {description ? (
          <div id={descriptionId} className="mt-xs text-sm text-muted">
            {description}
          </div>
        ) : null}
        {children ? <div className="mt-md">{children}</div> : null}
        <div className="mt-lg flex justify-end gap-xs">
          <Button variant="secondary" onClick={onClose} disabled={isConfirming}>
            {cancelLabel}
          </Button>
          <Button
            variant={tone === "danger" ? "danger" : "primary"}
            onClick={onConfirm}
            isLoading={isConfirming}
            disabled={confirmDisabled}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </dialog>
  );
}
