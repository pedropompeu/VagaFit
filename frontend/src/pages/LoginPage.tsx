import { useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate, type Location } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { AuthShell } from "../components/layout/AuthShell";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Field } from "../components/ui/Field";
import { Input } from "../components/ui/Input";
import { getApiErrorMessage } from "../lib/errors";
import { usePageTitle } from "../lib/usePageTitle";

interface LoginLocationState {
  from?: Location;
  notice?: string;
}

export function LoginPage() {
  usePageTitle("Entrar");

  const { login, sessionExpired } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const state = (location.state as LoginLocationState | null) ?? {};

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [notice, setNotice] = useState<string | null>(state.notice ?? null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice(null);
    setError(null);
    setIsSubmitting(true);

    try {
      await login(email.trim(), password);
      const target = state.from
        ? `${state.from.pathname}${state.from.search}${state.from.hash}`
        : "/curriculos";
      navigate(target, { replace: true });
    } catch (submitError) {
      setError(getApiErrorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthShell title="Entrar" description="Acesse sua conta para continuar de onde parou.">
      {notice ? (
        <div className="mb-md">
          <Alert variant="success">{notice}</Alert>
        </div>
      ) : sessionExpired ? (
        <div className="mb-md">
          <Alert variant="info">Sua sessão expirou. Entre de novo para continuar.</Alert>
        </div>
      ) : null}

      <form onSubmit={(event) => void handleSubmit(event)} className="flex flex-col gap-md">
        {error ? <Alert variant="error">{error}</Alert> : null}

        <Field label="E-mail" htmlFor="email" required>
          <Input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </Field>

        <Field label="Senha" htmlFor="password" required>
          <Input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
            required
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </Field>

        <Button type="submit" isLoading={isSubmitting} className="w-full">
          Entrar
        </Button>
      </form>

      <p className="mt-lg text-sm text-muted">
        Ainda não tem conta?{" "}
        <Link to="/criar-conta" className="font-medium text-brand hover:underline">
          Criar conta
        </Link>
      </p>
    </AuthShell>
  );
}
