import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import * as services from "../../services";
import { useCustomers } from "../../hooks/use-customers";
import type { Customer } from "../../types";

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  return function Wrapper({ children }: { children: ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
  };
}

afterEach(() => {
  vi.restoreAllMocks();
});

describe("useCustomers", () => {
  it("builds local search and pagination from the raw customer list", async () => {
    const firstCustomer = {
      id: "customer-1",
      name: "Acme",
      contactPersonName: null,
      contactPersonPhone: null,
      email: "ops@acme.com",
      notificationsEnabled: true,
      gemFuryUsed: true,
      customerSymbol: "ACME",
      createdAt: "2026-04-01T10:00:00.000Z",
      modifiedAt: "2026-04-01T10:00:00.000Z",
    } satisfies Customer;

    const secondCustomer = {
      ...firstCustomer,
      id: "customer-2",
      name: "Acme Europe",
      email: "europe@acme.com",
      customerSymbol: "ACMEEU",
    } satisfies Customer;

    vi.spyOn(services, "listCustomers").mockResolvedValue([
      firstCustomer,
      secondCustomer,
    ]);

    const { result } = renderHook(
      () => useCustomers({ search: "acme", page: 2, size: 1 }),
      {
        wrapper: createWrapper(),
      },
    );

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.items).toEqual([secondCustomer]);
    expect(result.current.pagination).toEqual({
      items: [secondCustomer],
      total: 2,
      page: 2,
      size: 1,
      pages: 2,
    });
    expect(result.current.isEmpty).toBe(false);
  });
});
