import axios from "axios";

interface ApiErrorPayload {
  error?: {
    code?: string;
    message?: string;
  };
}

const CONNECTION_MESSAGE =
  "Não foi possível conectar ao servidor. Verifique sua conexão e tente novamente.";

const GENERIC_MESSAGE = "Não foi possível concluir a solicitação. Tente novamente.";

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const payload = error.response?.data as ApiErrorPayload | undefined;
    const message = payload?.error?.message;
    if (typeof message === "string" && message.trim().length > 0) return message;

    if (!error.response) return CONNECTION_MESSAGE;

    const status = error.response.status;
    if (status === 413) return "O arquivo passa do limite de 5 MB.";
    if (status === 415) return "Envie um arquivo PDF.";
    if (status === 429) return "Muitas tentativas seguidas. Aguarde um instante e tente novamente.";
    if (status === 404) return "Não encontramos o que você procura.";
    return GENERIC_MESSAGE;
  }

  if (error instanceof Error && error.message.trim().length > 0) return error.message;
  return GENERIC_MESSAGE;
}

/** Erros 4xx não devem ser repetidos automaticamente pelo TanStack Query. */
export function isClientError(error: unknown): boolean {
  if (!axios.isAxiosError(error)) return false;
  const status = error.response?.status;
  return typeof status === "number" && status >= 400 && status < 500;
}
