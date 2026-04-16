export type AuthState = {
  isAuthenticated: boolean;
  isLoading: boolean;
};

export function useAuthState(): AuthState {
  return {
    isAuthenticated: true,
    isLoading: false,
  };
}
