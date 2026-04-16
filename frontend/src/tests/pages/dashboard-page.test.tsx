import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DashboardPage } from "../../pages/DashboardPage";
import * as services from "../../services";
import type { DashboardOverview } from "../../types";

function renderWithQueryClient(ui: ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>,
  );
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("DashboardPage", () => {
  it("renders operational metrics from the dashboard endpoint", async () => {
    vi.spyOn(services, "getDashboardOverview").mockResolvedValue({
      health: {
        status: "ok",
        services: { postgres: "ok", keyVault: "ok" },
      },
      metrics: {
        activeLicenses: 2,
        archivedLicenses: 1,
        expiringSoonLicenses: 1,
        expiredLicenses: 1,
        customers: 1,
        products: 1,
        licenseKinds: 1,
        appPackages: 1,
        auditEvents: 1,
      },
      serviceStates: [
        { name: "PostgreSQL", status: "ok" },
        { name: "Key Vault", status: "ok" },
      ],
      attention: ["1 active license(s) already expired."],
      latestAuditAt: "2026-04-15T06:00:00.000Z",
      refreshedAt: "2026-04-16T06:00:00.000Z",
    } satisfies DashboardOverview);

    renderWithQueryClient(<DashboardPage />);

    expect(
      await screen.findByRole("heading", { name: "System status: Healthy" }),
    ).toBeInTheDocument();

    expect(screen.getByTestId("metric-active-licenses")).toHaveTextContent("2");
    expect(screen.getByTestId("metric-archived-licenses")).toHaveTextContent(
      "1",
    );
    expect(screen.getByTestId("metric-customers")).toHaveTextContent("1");
    expect(screen.getByTestId("metric-products")).toHaveTextContent("1");
    expect(screen.getByTestId("metric-app-packages")).toHaveTextContent("1");
    expect(screen.getByTestId("metric-audit-events")).toHaveTextContent("1");
  });

  it("renders an error state when dashboard data fetch fails", async () => {
    vi.spyOn(services, "getDashboardOverview").mockRejectedValue({
      message: "Dashboard endpoint is unavailable",
      status: 503,
      code: "SERVICE_UNAVAILABLE",
    });

    renderWithQueryClient(<DashboardPage />);

    expect(
      await screen.findByRole("heading", { name: "Unable to load dashboard" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Dashboard endpoint is unavailable"),
    ).toBeInTheDocument();
  });
});
