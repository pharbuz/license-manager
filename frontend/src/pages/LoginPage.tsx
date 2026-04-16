import { useMemo } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth";
import { LoadingState } from "../components/common";

type LoginLocationState = {
  from?: {
    pathname?: string;
    search?: string;
    hash?: string;
  };
};

export function LoginPage() {
  const location = useLocation();
  const { isInitialized, isAuthenticated, login, error } = useAuth();

  const redirectPath = useMemo(() => {
    const state = location.state as LoginLocationState | null;
    const pathname = state?.from?.pathname;
    const search = state?.from?.search ?? "";
    const hash = state?.from?.hash ?? "";

    if (!pathname || pathname === "/login") {
      return "/";
    }

    return `${pathname}${search}${hash}`;
  }, [location.state]);

  if (!isInitialized) {
    return (
      <LoadingState
        title="Preparing sign-in"
        description="Checking for an existing Keycloak session."
      />
    );
  }

  if (isAuthenticated) {
    return <Navigate to={redirectPath} replace />;
  }

  return (
    <section className="login-page">
      <div className="login-page__card">
        <span className="login-page__pill">Keycloak Authentication</span>
        <h1>Sign in to License Manager</h1>
        <p>
          Use your organization account to continue. You will be redirected to
          the Keycloak login screen.
        </p>
        {error ? <p role="alert">{error}</p> : null}
        <button
          className="login-page__button"
          type="button"
          onClick={() => void login(redirectPath)}
        >
          Continue with Keycloak
        </button>
      </div>
    </section>
  );
}
