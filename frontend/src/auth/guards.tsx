import { Navigate, Outlet, useLocation } from "react-router-dom";

import { PageLoader } from "../components/ui/PageLoader";
import { useAuth } from "./AuthContext";

export function RequireAuth() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === "loading") return <PageLoader fullScreen label="Restaurando sua sessão…" />;
  if (status === "anonymous") {
    return <Navigate to="/entrar" replace state={{ from: location }} />;
  }
  return <Outlet />;
}

export function PublicOnly() {
  const { status } = useAuth();
  const location = useLocation();

  if (status === "loading") return <PageLoader fullScreen label="Restaurando sua sessão…" />;
  if (status === "authenticated") {
    // Após apagar a conta, a tela de login precisa aparecer mesmo que o estado
    // de autenticação ainda esteja sendo atualizado no mesmo instante.
    const state = location.state as { notice?: string } | null;
    if (!state?.notice) return <Navigate to="/curriculos" replace />;
  }
  return <Outlet />;
}
