import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { AuthShell } from "../components/layout/AuthShell";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Field } from "../components/ui/Field";
import { Input } from "../components/ui/Input";
import { getApiErrorMessage } from "../lib/errors";
import { usePageTitle } from "../lib/usePageTitle";

export function RegisterPage() {
  usePageTitle("Criar conta");

  const { register } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (password.length < 8) {
      setError("A senha precisa ter pelo menos 8 caracteres.");
      return;
    }
    if (password !== confirmation) {
      setError("As senhas não coincidem.");
      return;
    }

    setIsSubmitting(true);
    try {
      await register(email.trim(), password);
      navigate("/curriculos", { replace: true });
    } catch (submitError) {
      setError(getApiErrorMessage(submitError));
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthShell
      title="Criar conta"
      description="Leva menos de um minuto. Depois você já pode cadastrar seu primeiro currículo."
    >
      <form onSubmit={(event) => void handleSubmit(event)} className="flex flex-col gap-md">
        {error ? <Alert variant="error">{error}</Alert> : null}

        <Field label="E-mail" htmlFor="email" required>
          <Input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            required
            maxLength={254}
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />
        </Field>

        <Field
          label="Senha"
          htmlFor="password"
          required
          hint="Use pelo menos 8 caracteres."
        >
          <Input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            maxLength={128}
            aria-describedby="password-hint"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </Field>

        <Field label="Confirmar senha" htmlFor="password-confirmation" required>
          <Input
            id="password-confirmation"
            name="password-confirmation"
            type="password"
            autoComplete="new-password"
            required
            minLength={8}
            maxLength={128}
            value={confirmation}
            onChange={(event) => setConfirmation(event.target.value)}
          />
        </Field>

        <Button type="submit" isLoading={isSubmitting} className="w-full">
          Criar conta
        </Button>
      </form>

      <p className="mt-lg text-sm text-muted">
        Já tem conta?{" "}
        <Link to="/entrar" className="font-medium text-brand hover:underline">
          Entrar
        </Link>
      </p>
    </AuthShell>
  );
}
