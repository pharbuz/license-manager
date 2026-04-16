import { Navigate, Outlet, useLocation } from "react-router-dom";
import { LoadingState } from "../common";
import { useAuthState } from "../../features/auth/useAuthState";

export function ProtectedRoute() {
  const location = useLocation();
  const { isAuthenticated, isLoading } = useAuthState();

  if (isLoading) {
    return (
      <LoadingState
        title="Loading application"
        description="Checking your access and preparing the dashboard shell."
      />
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
