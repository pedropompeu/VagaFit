/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Origem da API, sem o sufixo `/api/v1`. Ex.: http://localhost:8000 */
  readonly VITE_API_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
