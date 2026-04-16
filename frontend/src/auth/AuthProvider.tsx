import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type PropsWithChildren,
} from "react";
import type Keycloak from "keycloak-js";
import type { KeycloakTokenParsed } from "keycloak-js";
import { getKeycloak, initKeycloak } from "./keycloak";
import {
  ensureFreshToken,
  setAuthClient,
  setAuthFailureHandler,
} from "./auth-session";
import { AuthContext, type AuthContextValue } from "./auth-context";
import { ErrorState, LoadingState } from "../components/common";

type AuthState = {
  isInitialized: boolean;
  isAuthenticated: boolean;
  token: string | null;
  user: AuthContextValue["user"];
  roles: string[];
  claims: Record<string, unknown>;
};

const initialAuthState: AuthState = {
  isInitialized: false,
  isAuthenticated: false,
  token: null,
  user: null,
  roles: [],
  claims: {},
};

function hasAuthCallbackParams(url: URL): boolean {
  return (
    url.searchParams.has("code") ||
    url.searchParams.has("state") ||
    url.searchParams.has("session_state")
  );
}

function createRedirectUri(path?: string): string {
  if (!path) {
    return window.location.href;
  }

  const url = new URL(path, window.location.origin);
  return url.toString();
}

function readRoles(
  keycloak: Keycloak,
  tokenParsed: KeycloakTokenParsed,
): string[] {
  const realmRoles = tokenParsed.realm_access?.roles ?? [];
  const resourceRoles =
    tokenParsed.resource_access?.[keycloak.clientId ?? ""]?.roles ?? [];

  return [...new Set([...realmRoles, ...resourceRoles])].sort();
}

function mapAuthState(keycloak: Keycloak): AuthState {
  const tokenParsed = keycloak.tokenParsed;

  if (!keycloak.authenticated || !keycloak.token || !tokenParsed) {
    return {
      ...initialAuthState,
      isInitialized: true,
    };
  }

  return {
    isInitialized: true,
    isAuthenticated: true,
    token: keycloak.token,
    user: {
      id: tokenParsed.sub ?? null,
      username: tokenParsed.preferred_username ?? null,
      name: tokenParsed.name ?? null,
      email: tokenParsed.email ?? null,
    },
    roles: readRoles(keycloak, tokenParsed),
    claims: tokenParsed,
  };
}

export function AuthProvider({ children }: PropsWithChildren) {
  const [authState, setAuthState] = useState<AuthState>(initialAuthState);
  const [authError, setAuthError] = useState<string | null>(null);
  const refreshTimerRef = useRef<number | null>(null);

  const syncAuthState = useCallback((client: Keycloak) => {
    setAuthState(mapAuthState(client));
  }, []);

  const handleAuthFailure = useCallback(() => {
    setAuthState({
      ...initialAuthState,
      isInitialized: true,
    });

    try {
      const keycloak = getKeycloak();
      void keycloak.clearToken();
    } catch (error) {
      setAuthError(
        error instanceof Error
          ? error.message
          : "Keycloak authentication configuration is invalid.",
      );
    }
    if (window.location.pathname !== "/login") {
      window.location.replace("/login");
    }
  }, []);

  useEffect(() => {
    let keycloak: Keycloak;
    try {
      keycloak = getKeycloak();
    } catch (error) {
      setAuthState({
        ...initialAuthState,
        isInitialized: true,
      });
      setAuthError(
        error instanceof Error
          ? error.message
          : "Keycloak authentication configuration is invalid.",
      );
      return;
    }

    setAuthClient(keycloak);
    setAuthFailureHandler(handleAuthFailure);

    let isMounted = true;

    const initAuth = async () => {
      let authenticated = false;
      try {
        authenticated = await initKeycloak({
          onLoad: "check-sso",
          pkceMethod: "S256",
          checkLoginIframe: false,
        });
      } catch (error) {
        setAuthError(
          error instanceof Error
            ? error.message
            : "Keycloak initialization failed.",
        );
      } finally {
        const currentUrl = new URL(window.location.href);
        if (!authenticated && hasAuthCallbackParams(currentUrl)) {
          setAuthError(
            "Login callback was received, but no authenticated session was created. Check Keycloak client type and redirect URI.",
          );
        }

        if (currentUrl.searchParams.has("code")) {
          currentUrl.searchParams.delete("code");
          currentUrl.searchParams.delete("state");
          currentUrl.searchParams.delete("session_state");
          window.history.replaceState(
            null,
            document.title,
            `${currentUrl.pathname}${currentUrl.search}${currentUrl.hash}`,
          );
        }

        if (isMounted) {
          syncAuthState(keycloak);
        }
      }
    };

    void initAuth();

    keycloak.onAuthSuccess = () => syncAuthState(keycloak);
    keycloak.onAuthRefreshSuccess = () => syncAuthState(keycloak);
    keycloak.onAuthLogout = () => syncAuthState(keycloak);
    keycloak.onAuthError = handleAuthFailure;
    keycloak.onAuthRefreshError = handleAuthFailure;
    keycloak.onTokenExpired = () => {
      void ensureFreshToken().catch(() => undefined);
    };

    refreshTimerRef.current = window.setInterval(() => {
      void ensureFreshToken().catch(() => undefined);
    }, 30000);

    return () => {
      isMounted = false;
      setAuthClient(null);
      setAuthFailureHandler(null);

      if (refreshTimerRef.current !== null) {
        window.clearInterval(refreshTimerRef.current);
      }

      keycloak.onAuthSuccess = undefined;
      keycloak.onAuthRefreshSuccess = undefined;
      keycloak.onAuthLogout = undefined;
      keycloak.onAuthError = undefined;
      keycloak.onAuthRefreshError = undefined;
      keycloak.onTokenExpired = undefined;
    };
  }, [handleAuthFailure, syncAuthState]);

  const login = useCallback(async (redirectPath?: string) => {
    try {
      const keycloak = getKeycloak();
      await keycloak.login({ redirectUri: createRedirectUri(redirectPath) });
    } catch (error) {
      setAuthError(
        error instanceof Error
          ? error.message
          : "Keycloak authentication configuration is invalid.",
      );
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      const keycloak = getKeycloak();
      await keycloak.logout({ redirectUri: createRedirectUri("/login") });
    } catch (error) {
      setAuthError(
        error instanceof Error
          ? error.message
          : "Keycloak authentication configuration is invalid.",
      );
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      ...authState,
      error: authError,
      login,
      logout,
    }),
    [authError, authState, login, logout],
  );

  if (!authState.isInitialized) {
    return (
      <LoadingState
        title="Initializing authentication"
        description="Connecting to Keycloak and restoring your session."
      />
    );
  }

  if (
    authError &&
    !authState.isAuthenticated &&
    window.location.pathname !== "/login"
  ) {
    return (
      <ErrorState title="Authentication Setup Error" description={authError} />
    );
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
