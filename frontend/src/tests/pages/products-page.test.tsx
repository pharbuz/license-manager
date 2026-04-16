import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import * as services from "../../services";
import { ProductsPage } from "../../pages/ProductsPage";
import type { Product } from "../../types";

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

describe("ProductsPage", () => {
  it("renders product rows", async () => {
    const product = {
      id: "product-1",
      name: "Platform",
      kind: "Core",
      createdAt: "2026-04-01T10:00:00.000Z",
      modifiedAt: "2026-04-01T10:00:00.000Z",
    } satisfies Product;

    vi.spyOn(services, "listProducts").mockResolvedValue([product]);

    renderWithQueryClient(<ProductsPage />);

    expect(
      await screen.findByRole("heading", { name: "Products" }),
    ).toBeInTheDocument();
    expect(await screen.findByText("Platform")).toBeInTheDocument();
  });
});
