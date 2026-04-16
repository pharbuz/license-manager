import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import type { ReactElement } from "react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import * as services from "../../services";
import { CustomersPage } from "../../pages/CustomersPage";
import type { Customer } from "../../types";

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

describe("CustomersPage", () => {
  it("renders customers from the raw list contract", async () => {
    const customer = {
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

    vi.spyOn(services, "listCustomers").mockResolvedValue([customer]);

    renderWithQueryClient(<CustomersPage />);

    expect(
      await screen.findByRole("heading", { name: "Customers" }),
    ).toBeInTheDocument();
    expect(await screen.findByText("ACME")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Add customer" }),
    ).toBeInTheDocument();
  });

  it("opens the create modal and submits a new customer", async () => {
    const user = userEvent.setup();

    vi.spyOn(services, "listCustomers").mockResolvedValue([]);

    const createSpy = vi
      .spyOn(services, "createCustomer")
      .mockResolvedValue({} as Customer);

    renderWithQueryClient(<CustomersPage />);

    await user.click(
      await screen.findByRole("button", { name: "Add customer" }),
    );

    await user.type(screen.getByLabelText("Name"), "Acme");
    await user.type(screen.getByLabelText("Email"), "ops@acme.com");
    await user.type(screen.getByLabelText("Customer symbol"), "ACME");
    await user.click(screen.getByRole("button", { name: "Create customer" }));

    await waitFor(() => expect(createSpy).toHaveBeenCalled());
    expect(createSpy).toHaveBeenCalledWith(
      expect.objectContaining({
        name: "Acme",
        email: "ops@acme.com",
        customerSymbol: "ACME",
      }),
    );
  });
});
