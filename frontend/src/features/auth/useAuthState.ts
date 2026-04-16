import { useAuth } from "../../auth";

export type AuthState = {
  isAuthenticated: boolean;
  isLoading: boolean;
};

export function useAuthState(): AuthState {
  const { isAuthenticated, isInitialized } = useAuth();
  return {
    isAuthenticated,
    isLoading: !isInitialized,
  };
}
