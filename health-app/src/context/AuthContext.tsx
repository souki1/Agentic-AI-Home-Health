import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

import type { AuthResponse, AuthState } from "../types";

export const AUTH_STORAGE_KEY = "health_analytics_auth";

function loadAuth(): AuthState | null {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (raw) {
      return JSON.parse(raw) as AuthState;
    }
  } catch {
    // ignore corrupted storage
  }
  return null;
}

function saveAuth(auth: AuthState | null) {
  if (auth) localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(auth));
  else localStorage.removeItem(AUTH_STORAGE_KEY);
}

interface AuthContextValue {
  auth: AuthState | null;
  user: AuthState["user"] | null;
  login: (response: AuthResponse) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState<AuthState | null>(loadAuth);

  const login = useCallback((response: AuthResponse) => {
    const next: AuthState = { token: response.token, user: response.user };
    setAuth(next);
    saveAuth(next);
  }, []);

  const logout = useCallback(() => {
    setAuth(null);
    saveAuth(null);
  }, []);

  const user = auth?.user ?? null;
  return <AuthContext.Provider value={{ auth, user, login, logout }}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
