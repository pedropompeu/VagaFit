import { useMutation } from "@tanstack/react-query";
import { useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../auth/AuthContext";
import { Alert } from "../components/ui/Alert";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { ConfirmDialog } from "../components/ui/ConfirmDialog";
import { Field } from "../components/ui/Field";
import { Input } from "../components/ui/Input";
import { PageHeader } from "../components/ui/PageHeader";
import { getApiErrorMessage } from "../lib/errors";
import { formatDateTime } from "../lib/format";
import { usePageTitle } from "../lib/usePageTitle";

export function SettingsPage() {
  usePageTitle("Configurações");

  const { user, deleteAccount } = useAuth();
  const navigate = useNavigate();
  const emailInputRef = useRef<HTMLInputElement>(null);

  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [emailConfirmation, setEmailConfirmation] = useState("");
  const [password, setPassword] = useState("");
  const [formError, setFormError] = useState<string | null>(null);

  const deleteMutation = useMutation({
    mutationFn: deleteAccount,
    onSuccess: () => {
      navigate("/entrar", {
        replace: true,
        state: { notice: "Sua conta foi apagada. Sentiremos sua falta." },
      });
    },
  });

  function openDeleteDialog() {
    deleteMutation.reset();
    setEmailConfirmation("");
    setPassword("");
    setFormError(null);
    setIsDeleteOpen(true);
  }

  function closeDeleteDialog() {
    if (deleteMutation.isPending) return;
    setIsDeleteOpen(false);
    deleteMutation.reset();
    setFormError(null);
    setPassword("");
  }

  function handleConfirmDelete() {
    setFormError(null);

    if (!user) {
      setFormError("Não foi possível identificar sua conta. Entre novamente.");
      return;
    }
    if (emailConfirmation.trim().toLowerCase() !== user.email.toLowerCase()) {
      setFormError("Digite o e-mail da conta para confirmar.");
      return;
    }
    if (password.length === 0) {
      setFormError("Informe sua senha atual.");
      return;
    }

    deleteMutation.mutate(password);
  }

  const deleteError =
    formError ?? (deleteMutation.isError ? getApiErrorMessage(deleteMutation.error) : null);

  return (
    <>
      <PageHeader
        title="Configurações"
        description="Gerencie sua conta e os dados salvos no VagaFit."
      />

      <div className="flex flex-col gap-lg">
        <Card className="p-lg">
          <h2 className="text-base font-semibold text-ink">Conta</h2>
          <dl className="mt-sm grid gap-md sm:grid-cols-2">
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-muted">E-mail</dt>
              <dd className="mt-2xs break-all text-sm text-ink">{user?.email ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-xs font-medium uppercase tracking-wide text-muted">
                Conta criada em
              </dt>
              <dd className="mt-2xs text-sm text-ink">
                {user ? formatDateTime(user.created_at) : "—"}
              </dd>
            </div>
          </dl>
        </Card>

        <Card className="border-danger p-lg">
          <h2 className="text-base font-semibold text-danger">Apagar minha conta</h2>
          <p className="mt-xs max-w-2xl text-sm text-muted">
            A exclusão é definitiva e remove seus currículos, vagas e dados vinculados. Para
            confirmar, você precisa digitar o e-mail da conta e a senha atual.
          </p>
          <Button variant="danger" className="mt-md" onClick={openDeleteDialog}>
            Apagar minha conta
          </Button>
        </Card>
      </div>

      <ConfirmDialog
        open={isDeleteOpen}
        title="Apagar minha conta?"
        description="Todos os seus currículos, vagas e dados vinculados serão apagados definitivamente. Esta ação não pode ser desfeita."
        confirmLabel="Apagar conta"
        tone="danger"
        isConfirming={deleteMutation.isPending}
        initialFocusRef={emailInputRef}
        onClose={closeDeleteDialog}
        onConfirm={handleConfirmDelete}
      >
        <div className="flex flex-col gap-md">
          {deleteError ? <Alert variant="error">{deleteError}</Alert> : null}

          <Field
            label="E-mail da conta"
            htmlFor="delete-email"
            required
            hint={user ? `Digite ${user.email} para confirmar.` : undefined}
          >
            <Input
              ref={emailInputRef}
              id="delete-email"
              name="delete-email"
              type="email"
              autoComplete="off"
              required
              disabled={deleteMutation.isPending}
              value={emailConfirmation}
              onChange={(event) => {
                setEmailConfirmation(event.target.value);
                setFormError(null);
              }}
            />
          </Field>

          <Field label="Senha atual" htmlFor="delete-password" required>
            <Input
              id="delete-password"
              name="delete-password"
              type="password"
              autoComplete="current-password"
              required
              disabled={deleteMutation.isPending}
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
                setFormError(null);
              }}
            />
          </Field>
        </div>
      </ConfirmDialog>
    </>
  );
}
