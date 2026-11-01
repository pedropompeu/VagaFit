import { useQueryClient } from "@tanstack/react-query";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { deleteAccountRequest, loginRequest, logoutRequest, registerRequest } from "../api/auth";
import { refreshSession, setAccessToken, setSessionExpiredHandler } from "../api/client";
import type { AuthResponse, User } from "../types/api";

export type AuthStatus = "loading" | "authenticated" | "anonymous";

interface AuthContextValue {
  user: User | null;
  status: AuthStatus;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  deleteAccount: (password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

// Uma única restauração de sessão por carregamento, mesmo com o StrictMode
// montando o efeito duas vezes. Refresh repetido giraria o token de novo.
let bootstrapPromise: Promise<User | null> | null = null;

function bootstrapSession(): Promise<User | null> {
  if (!bootstrapPromise) {
    bootstrapPromise = refreshSession()
      .then((session) => session.user)
      .catch(() => {
        setAccessToken(null);
        return null;
      });
  }
  return bootstrapPromise;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient();
  const [user, setUser] = useState<User | null>(null);
  const [status, setStatus] = useState<AuthStatus>("loading");

  useEffect(() => {
    let active = true;
    void bootstrapSession().then((restoredUser) => {
      if (!active) return;
      setUser(restoredUser);
      setStatus(restoredUser ? "authenticated" : "anonymous");
    });
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    setSessionExpiredHandler(() => {
      setUser(null);
      setStatus("anonymous");
      queryClient.clear();
    });
    return () => {
      setSessionExpiredHandler(null);
    };
  }, [queryClient]);

  const applySession = useCallback(
    (session: AuthResponse) => {
      setAccessToken(session.access_token);
      setUser(session.user);
      setStatus("authenticated");
      queryClient.clear();
    },
    [queryClient],
  );

  const login = useCallback(
    async (email: string, password: string) => {
      applySession(await loginRequest(email, password));
    },
    [applySession],
  );

  const register = useCallback(
    async (email: string, password: string) => {
      applySession(await registerRequest(email, password));
    },
    [applySession],
  );

  const logout = useCallback(async () => {
    try {
      await logoutRequest();
    } catch {
      // A sessão local é encerrada mesmo que a API não responda.
    }
    setAccessToken(null);
    setUser(null);
    setStatus("anonymous");
    queryClient.clear();
  }, [queryClient]);

  const deleteAccount = useCallback(
    async (password: string) => {
      await deleteAccountRequest(password);
      setAccessToken(null);
      setUser(null);
      setStatus("anonymous");
      queryClient.clear();
    },
    [queryClient],
  );

  const value = useMemo<AuthContextValue>(
    () => ({ user, status, login, register, logout, deleteAccount }),
    [user, status, login, register, logout, deleteAccount],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth precisa estar dentro de AuthProvider.");
  return context;
}
