import { createContext } from "react";

type UserInfo = {
  id: string | null;
  username: string | null;
  name: string | null;
  email: string | null;
};

export type AuthContextValue = {
  isInitialized: boolean;
  isAuthenticated: boolean;
  error: string | null;
  token: string | null;
  user: UserInfo | null;
  roles: string[];
  claims: Record<string, unknown>;
  login: (redirectPath?: string) => Promise<void>;
  logout: () => Promise<void>;
};

export const AuthContext = createContext<AuthContextValue | null>(null);
