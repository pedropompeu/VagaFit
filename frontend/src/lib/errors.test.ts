import { AxiosError, AxiosHeaders, type AxiosResponse } from "axios";
import { describe, expect, it } from "vitest";

import { getApiErrorMessage, isClientError } from "./errors";

function httpError(status: number, data: unknown = {}): AxiosError {
  const response = {
    status,
    data,
    statusText: "",
    headers: {},
    config: { headers: new AxiosHeaders() },
  } as AxiosResponse;
  return new AxiosError("falhou", "ERR_BAD_RESPONSE", undefined, undefined, response);
}

describe("getApiErrorMessage", () => {
  it("usa a mensagem que a API mandou", () => {
    const error = httpError(409, { error: { code: "conflict", message: "E-mail já cadastrado." } });
    expect(getApiErrorMessage(error)).toBe("E-mail já cadastrado.");
  });

  it("traduz status conhecidos quando a API não manda mensagem", () => {
    expect(getApiErrorMessage(httpError(413))).toBe("O arquivo passa do limite de 5 MB.");
    expect(getApiErrorMessage(httpError(415))).toBe("Envie um arquivo PDF.");
    expect(getApiErrorMessage(httpError(429))).toMatch(/Muitas tentativas/);
    expect(getApiErrorMessage(httpError(404))).toMatch(/Não encontramos/);
  });

  it("ignora mensagem vazia e cai no texto genérico", () => {
    const error = httpError(500, { error: { message: "   " } });
    expect(getApiErrorMessage(error)).toMatch(/Não foi possível concluir/);
  });

  it("explica falha de conexão quando não há resposta", () => {
    expect(getApiErrorMessage(new AxiosError("Network Error"))).toMatch(/conectar ao servidor/);
  });

  it("aceita Error comum e valor desconhecido", () => {
    expect(getApiErrorMessage(new Error("Arquivo inválido."))).toBe("Arquivo inválido.");
    expect(getApiErrorMessage("??")).toMatch(/Não foi possível concluir/);
  });
});

describe("isClientError", () => {
  it("é verdadeiro só para 4xx", () => {
    expect(isClientError(httpError(400))).toBe(true);
    expect(isClientError(httpError(499))).toBe(true);
    expect(isClientError(httpError(500))).toBe(false);
    expect(isClientError(new AxiosError("Network Error"))).toBe(false);
    expect(isClientError(new Error("x"))).toBe(false);
  });
});
