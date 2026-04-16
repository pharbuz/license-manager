import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import type { ReactElement } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import type { ApiError } from "../../api";
import { SmtpCredentialsPage } from "../../pages/SmtpCredentialsPage";
import * as services from "../../services";
import type { SmtpCredential } from "../../types";

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

describe("SmtpCredentialsPage", () => {
  it("shows an empty state when SMTP credentials are missing", async () => {
    vi.spyOn(services, "getSmtpCredentials").mockRejectedValue({
      message: "Request failed with status code 404",
      status: 404,
      code: "ERR_BAD_REQUEST",
    } satisfies ApiError);

    renderWithQueryClient(<SmtpCredentialsPage />);

    expect(
      await screen.findByRole("heading", {
        name: "No SMTP credentials configured",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Create credentials to enable outgoing notification emails.",
      ),
    ).toBeInTheDocument();
  });

  it("renders existing SMTP credentials details", async () => {
    vi.spyOn(services, "getSmtpCredentials").mockResolvedValue({
      secretName: "smtp-main",
      secretVersion: "1",
      host: "smtp.example.com",
      port: 587,
      username: "mailer",
      senderEmail: "noreply@example.com",
      useTls: true,
      useSsl: false,
      createdAt: "2026-04-01T10:00:00.000Z",
      modifiedAt: "2026-04-01T10:00:00.000Z",
    } satisfies SmtpCredential);

    renderWithQueryClient(<SmtpCredentialsPage />);

    expect(await screen.findByText("smtp.example.com")).toBeInTheDocument();
    expect(screen.getByText("noreply@example.com")).toBeInTheDocument();
  });

  it("shows an error state for non-404 API failures", async () => {
    vi.spyOn(services, "getSmtpCredentials").mockRejectedValue({
      message: "SMTP endpoint is unavailable",
      status: 503,
      code: "SERVICE_UNAVAILABLE",
    } satisfies ApiError);

    renderWithQueryClient(<SmtpCredentialsPage />);

    expect(
      await screen.findByRole("heading", {
        name: "Unable to load SMTP credentials",
      }),
    ).toBeInTheDocument();
    expect(
      screen.getByText("SMTP endpoint is unavailable"),
    ).toBeInTheDocument();
  });
});
