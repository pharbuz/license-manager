import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import * as services from "../../services";
import { AuditLogsPage } from "../../pages/AuditLogsPage";

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

describe("AuditLogsPage", () => {
  it("renders audit log filters and rows", async () => {
    vi.spyOn(services, "listAuditLogs").mockResolvedValue([
      {
        id: "audit-1",
        actorId: null,
        actorType: "system",
        actorDisplayName: null,
        source: "api",
        requestId: null,
        action: "created",
        entityType: "customer",
        entityId: "customer-1",
        summary: "Created customer",
        diff: null,
        metadata: null,
        occurredAt: "2026-04-01T10:00:00.000Z",
        recordedAt: "2026-04-01T10:00:00.000Z",
      },
    ]);

    renderWithQueryClient(<AuditLogsPage />);

    expect(
      await screen.findByRole("heading", { name: "Audit Logs" }),
    ).toBeInTheDocument();
    expect(await screen.findByText("Created customer")).toBeInTheDocument();
  });
});
