import { createBrowserRouter, Navigate } from "react-router-dom";
import { ProtectedRoute } from "../components/auth/ProtectedRoute";
import { AppShell } from "../layout/AppShell";
import { ArchivedLicensesPage } from "../pages/ArchivedLicensesPage";
import { AppPackagesPage } from "../pages/AppPackagesPage";
import { AuditLogsPage } from "../pages/AuditLogsPage";
import { CustomersPage } from "../pages/CustomersPage";
import { DashboardPage } from "../pages/DashboardPage";
import { LicenseKindsPage } from "../pages/LicenseKindsPage";
import { LicensesPage } from "../pages/LicensesPage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { ProductsPage } from "../pages/ProductsPage";
import { SmtpCredentialsPage } from "../pages/SmtpCredentialsPage";

export type NavItem = {
  label: string;
  to: string;
};

export const navItems: NavItem[] = [
  { label: "Dashboard", to: "/" },
  { label: "Licenses", to: "/licenses" },
  { label: "Archived Licenses", to: "/licenses/archived" },
  { label: "Customers", to: "/customers" },
  { label: "Products", to: "/products" },
  { label: "License Kinds", to: "/kinds" },
  { label: "App Packages", to: "/app-packages" },
  { label: "SMTP Credentials", to: "/smtp-credentials" },
  { label: "Audit Logs", to: "/audit/logs" },
];

export const appRouter = createBrowserRouter([
  {
    path: "/login",
    element: <LoginPage />,
  },
  {
    path: "/",
    element: <ProtectedRoute />,
    children: [
      {
        path: "/",
        element: <AppShell />,
        children: [
          { index: true, element: <DashboardPage /> },
          { path: "licenses", element: <LicensesPage /> },
          { path: "licenses/archived", element: <ArchivedLicensesPage /> },
          { path: "customers", element: <CustomersPage /> },
          { path: "products", element: <ProductsPage /> },
          { path: "kinds", element: <LicenseKindsPage /> },
          { path: "app-packages", element: <AppPackagesPage /> },
          { path: "smtp-credentials", element: <SmtpCredentialsPage /> },
          { path: "audit/logs", element: <AuditLogsPage /> },
          { path: "*", element: <NotFoundPage /> },
        ],
      },
    ],
  },
  {
    path: "*",
    element: <Navigate to="/" replace />,
  },
]);
