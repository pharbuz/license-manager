import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { App } from "../app/app";
import * as services from "../services";

beforeEach(() => {
  vi.spyOn(services, "getHealth").mockResolvedValue({
    status: "ok",
    services: { postgres: "ok", keyVault: "ok" },
  });
  vi.spyOn(services, "listLicenses").mockResolvedValue([]);
  vi.spyOn(services, "listArchivedLicenses").mockResolvedValue([]);
  vi.spyOn(services, "listCustomers").mockResolvedValue([]);
  vi.spyOn(services, "listProducts").mockResolvedValue([]);
  vi.spyOn(services, "listAppPackages").mockResolvedValue([]);
  vi.spyOn(services, "listAuditLogs").mockResolvedValue([]);
});

describe("Stage 1 bootstrap", () => {
  it("renders the shell and default dashboard route", async () => {
    render(<App />);

    expect(await screen.findByText("License Manager")).toBeInTheDocument();
    expect(await screen.findByText("System status")).toBeInTheDocument();
    expect(
      await screen.findByRole("heading", { name: "Dashboard" }),
    ).toBeInTheDocument();
  });

  it("includes routes for OpenAPI-backed domains in navigation", async () => {
    render(<App />);

    expect(
      await screen.findByRole("link", { name: "Licenses" }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("link", { name: "Customers" }),
    ).toBeInTheDocument();
    expect(
      await screen.findByRole("link", { name: "Audit Logs" }),
    ).toBeInTheDocument();
  });

  it("opens the user dropdown menu", async () => {
    const user = userEvent.setup();

    render(<App />);

    await user.click(await screen.findByRole("button", { name: "User menu" }));

    expect(await screen.findByText(/Dark mode|Light mode/)).toBeInTheDocument();
    expect(await screen.findByText("Logout")).toBeInTheDocument();
  });
});
