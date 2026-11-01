import { useEffect, useState } from "react";

import { Button } from "../ui/Button";

export function CopyButton({ text, label = "Copiar" }: { text: string; label?: string }) {
  const [state, setState] = useState<"idle" | "copied" | "failed">("idle");

  useEffect(() => {
    if (state === "idle") return;
    const timer = window.setTimeout(() => setState("idle"), 2000);
    return () => window.clearTimeout(timer);
  }, [state]);

  async function copy() {
    try {
      await navigator.clipboard.writeText(text);
      setState("copied");
    } catch {
      setState("failed");
    }
  }

  return (
    <Button variant="secondary" size="sm" onClick={() => void copy()} aria-live="polite">
      {state === "copied" ? "Copiado" : state === "failed" ? "Não deu para copiar" : label}
    </Button>
  );
}
