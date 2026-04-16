import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import type { ReactElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import * as services from "../../services";
import { LicensesPage } from "../../pages/LicensesPage";
import type { License } from "../../types";

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

describe("LicensesPage", () => {
  it("renders license rows and generate action", async () => {
    const license = {
      id: "license-1",
      customerId: null,
      productId: null,
      kindId: null,
      licenseCount: 1,
      licenseState: "active",
      licenseKey: "ABC-123",
      licenseEmail: "ops@acme.com",
      doubleSend: false,
      beginDate: "2026-04-01T10:00:00.000Z",
      endDate: "2026-04-30T10:00:00.000Z",
      notificationDate: "2026-04-20T10:00:00.000Z",
      createdAt: "2026-04-01T10:00:00.000Z",
      modifiedAt: "2026-04-01T10:00:00.000Z",
    } satisfies License;

    vi.spyOn(services, "listLicenses").mockResolvedValue([license]);
    vi.spyOn(services, "listDropdownItems")
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([]);

    renderWithQueryClient(<LicensesPage />);

    expect(
      await screen.findByRole("heading", { name: "Licenses" }),
    ).toBeInTheDocument();
    expect(await screen.findByText("ABC-123")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Generate key" }),
    ).toBeInTheDocument();
  });

  it("uses dropdown-backed selects in the license editor", async () => {
    const user = userEvent.setup();

    vi.spyOn(services, "listLicenses").mockResolvedValue([]);
    vi.spyOn(services, "listDropdownItems")
      .mockResolvedValueOnce([{ id: "customer-1", text: "ACM - Acme" }])
      .mockResolvedValueOnce([{ id: "product-1", text: "Gateway" }])
      .mockResolvedValueOnce([{ id: "kind-1", text: "Trial" }]);

    renderWithQueryClient(<LicensesPage />);

    await user.click(
      await screen.findByRole("button", { name: "Add license" }),
    );

    expect(await screen.findByLabelText("Customer")).toHaveDisplayValue(
      "Select customer",
    );
    expect(screen.getByLabelText("Product")).toHaveDisplayValue(
      "Select product",
    );
    expect(screen.getByLabelText("License kind")).toHaveDisplayValue(
      "Select license kind",
    );

    await user.selectOptions(screen.getByLabelText("Customer"), "customer-1");

    expect(screen.getByLabelText("Customer")).toHaveValue("customer-1");
  });
});
