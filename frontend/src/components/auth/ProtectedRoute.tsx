import { Navigate, Outlet, useLocation } from "react-router-dom";
import { LoadingState } from "../common";
import { useAuth } from "../../auth";

export function ProtectedRoute() {
  const location = useLocation();
  const { isAuthenticated, isInitialized } = useAuth();

  if (!isInitialized) {
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
