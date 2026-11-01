import { LinkButton } from "../components/ui/LinkButton";
import { Card } from "../components/ui/Card";
import { usePageTitle } from "../lib/usePageTitle";

export function NotFoundPage() {
  usePageTitle("Página não encontrada");

  return (
    <Card className="flex flex-col items-center gap-sm px-lg py-2xl text-center">
      <p className="text-sm font-semibold text-brand">404</p>
      <h1 className="text-2xl font-semibold tracking-tight text-ink">Página não encontrada</h1>
      <p className="max-w-md text-sm text-muted">
        O endereço que você abriu não existe ou foi movido. Volte para seus currículos para
        continuar.
      </p>
      <LinkButton to="/curriculos" className="mt-xs">
        Ir para currículos
      </LinkButton>
    </Card>
  );
}
