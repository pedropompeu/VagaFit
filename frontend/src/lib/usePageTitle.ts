import { useEffect } from "react";

/** Mantém o título da aba coerente com a tela atual. */
export function usePageTitle(title: string): void {
  useEffect(() => {
    document.title = `${title} · VagaFit`;
  }, [title]);
}
