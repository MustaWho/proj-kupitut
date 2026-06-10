import { createContext, useContext, useMemo, useState, type ReactNode } from "react";
import { api } from "../api/client";
import type { AuthResponse, User, UserRole } from "../types";
import { clearAuth, loadAuth, saveAuth } from "./storage";

type AuthState = {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (login: string, password: string) => Promise<void>;
  register: (payload: {
    email: string;
    username: string;
    password: string;
    role?: UserRole;
    first_name?: string;
    last_name?: string;
  }) => Promise<void>;
  updateUser: (user: User) => void;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

function toState(response: AuthResponse) {
  return {
    user: response.user,
    accessToken: response.access_token,
    refreshToken: response.refresh_token
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [auth, setAuth] = useState(() =>
    loadAuth<{ user: User; accessToken: string; refreshToken: string }>()
  );

  const value = useMemo<AuthState>(
    () => ({
      user: auth?.user ?? null,
      accessToken: auth?.accessToken ?? null,
      refreshToken: auth?.refreshToken ?? null,
      async login(loginValue, password) {
        const next = toState(await api.login({ login: loginValue, password }));
        setAuth(next);
        saveAuth(next);
      },
      async register(payload) {
        const next = toState(await api.register(payload));
        setAuth(next);
        saveAuth(next);
      },
      updateUser(user) {
        if (!auth) return;
        const next = { ...auth, user };
        setAuth(next);
        saveAuth(next);
      },
      logout() {
        setAuth(null);
        clearAuth();
      }
    }),
    [auth]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
