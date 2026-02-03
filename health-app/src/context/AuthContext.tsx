import { createContext, useContext, useState, useCallback, type ReactNode } from 'react';
import type { AuthUser, Role } from '../types';

const AUTH_KEY = 'health_analytics_auth';

function loadAuth(): AuthUser | null {
  try {
    const raw = localStorage.getItem(AUTH_KEY);
    if (raw) return JSON.parse(raw);
  } catch (_) {}
  return null;
}

function saveAuth(user: AuthUser | null) {
  if (user) localStorage.setItem(AUTH_KEY, JSON.stringify(user));
  else localStorage.removeItem(AUTH_KEY);
}

interface AuthContextValue {
  user: AuthUser | null;
  login: (email: string, role: Role) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(loadAuth);

  const login = useCallback((email: string, role: Role) => {
    const u = { email, role };
    setUser(u);
    saveAuth(u);
  }, []);

  const logout = useCallback(() => {
    setUser(null);
    saveAuth(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
