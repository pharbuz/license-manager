import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DashboardPage } from "../../pages/DashboardPage";
import * as services from "../../services";
import type {
  AppPackage,
  AuditLogEntry,
  Customer,
  License,
  Product,
} from "../../types";

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
  it("renders operational metrics from runtime endpoints", async () => {
    vi.spyOn(services, "getHealth").mockResolvedValue({
      status: "ok",
      services: { postgres: "ok", keyVault: "ok" },
    });

    vi.spyOn(services, "listLicenses").mockResolvedValue([
      {
        id: "license-1",
        customerId: "customer-1",
        productId: "product-1",
        kindId: "kind-1",
        licenseCount: 10,
        licenseState: "active",
        licenseKey: "KEY-1",
        licenseEmail: "ops@acme.com",
        doubleSend: false,
        beginDate: "2026-03-01T00:00:00.000Z",
        endDate: "2026-04-20T00:00:00.000Z",
        notificationDate: "2026-04-18T00:00:00.000Z",
        createdAt: "2026-03-01T00:00:00.000Z",
        modifiedAt: "2026-03-01T00:00:00.000Z",
      },
      {
        id: "license-2",
        customerId: "customer-1",
        productId: "product-1",
        kindId: "kind-1",
        licenseCount: 3,
        licenseState: "active",
        licenseKey: "KEY-2",
        licenseEmail: "ops@acme.com",
        doubleSend: false,
        beginDate: "2026-02-01T00:00:00.000Z",
        endDate: "2026-03-01T00:00:00.000Z",
        notificationDate: "2026-02-15T00:00:00.000Z",
        createdAt: "2026-02-01T00:00:00.000Z",
        modifiedAt: "2026-02-01T00:00:00.000Z",
      },
    ] satisfies License[]);

    vi.spyOn(services, "listArchivedLicenses").mockResolvedValue([
      {
        id: "license-archived",
        customerId: null,
        productId: null,
        kindId: null,
        licenseCount: 1,
        licenseState: "archived",
        licenseKey: "ARCHIVED-1",
        licenseEmail: "archived@acme.com",
        doubleSend: false,
        beginDate: "2025-01-01T00:00:00.000Z",
        endDate: "2025-12-31T00:00:00.000Z",
        notificationDate: "2025-12-01T00:00:00.000Z",
        createdAt: "2025-01-01T00:00:00.000Z",
        modifiedAt: "2025-01-01T00:00:00.000Z",
      },
    ] satisfies License[]);

    vi.spyOn(services, "listCustomers").mockResolvedValue([
      {
        id: "customer-1",
        name: "Acme",
        contactPersonName: null,
        contactPersonPhone: null,
        email: "ops@acme.com",
        notificationsEnabled: true,
        gemFuryUsed: true,
        customerSymbol: "ACME",
        createdAt: "2026-03-01T00:00:00.000Z",
        modifiedAt: "2026-03-01T00:00:00.000Z",
      },
    ] satisfies Customer[]);

    vi.spyOn(services, "listProducts").mockResolvedValue([
      {
        id: "product-1",
        name: "Gateway",
        kind: "core",
        createdAt: "2026-03-01T00:00:00.000Z",
        modifiedAt: "2026-03-01T00:00:00.000Z",
      },
    ] satisfies Product[]);

    vi.spyOn(services, "listAppPackages").mockResolvedValue([
      {
        id: "package-1",
        versionNumber: "1.0.0",
        binaryName: "gateway.zip",
        gemFuryUrl: "https://example.com/gem",
        binaryUrl: "https://example.com/binary",
        createdAt: "2026-03-01T00:00:00.000Z",
        modifiedAt: "2026-03-01T00:00:00.000Z",
      },
    ] satisfies AppPackage[]);

    vi.spyOn(services, "listAuditLogs").mockResolvedValue([
      {
        id: "audit-1",
        actorId: "user-1",
        actorType: "user",
        actorDisplayName: "Ops User",
        source: "ui",
        requestId: "request-1",
        action: "license.updated",
        entityType: "license",
        entityId: "license-1",
        summary: "Updated license",
        diff: null,
        metadata: null,
        occurredAt: "2026-04-15T06:00:00.000Z",
        recordedAt: "2026-04-15T06:00:00.000Z",
      },
    ] satisfies AuditLogEntry[]);

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
    vi.spyOn(services, "getHealth").mockRejectedValue({
      message: "Health endpoint is unavailable",
      status: 503,
      code: "SERVICE_UNAVAILABLE",
    });

    vi.spyOn(services, "listLicenses").mockResolvedValue([]);
    vi.spyOn(services, "listArchivedLicenses").mockResolvedValue([]);
    vi.spyOn(services, "listCustomers").mockResolvedValue([]);
    vi.spyOn(services, "listProducts").mockResolvedValue([]);
    vi.spyOn(services, "listAppPackages").mockResolvedValue([]);
    vi.spyOn(services, "listAuditLogs").mockResolvedValue([]);

    renderWithQueryClient(<DashboardPage />);

    expect(
      await screen.findByRole("heading", { name: "Unable to load dashboard" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("Health endpoint is unavailable"),
    ).toBeInTheDocument();
  });
});
