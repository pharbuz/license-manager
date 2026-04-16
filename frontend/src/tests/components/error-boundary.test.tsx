import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ErrorBoundary } from "../../components/common";

describe("ErrorBoundary", () => {
  let consoleErrorSpy: ReturnType<typeof vi.spyOn>;

  beforeEach(() => {
    consoleErrorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  it("shows a themed fallback and lets the user retry", async () => {
    const user = userEvent.setup();
    let shouldThrow = true;

    function FlakyView() {
      if (shouldThrow) {
        throw new Error("Dashboard exploded");
      }

      return <div>Recovered view</div>;
    }

    const { container } = render(
      <MemoryRouter initialEntries={["/broken"]}>
        <Routes>
          <Route
            path="/broken"
            element={
              <ErrorBoundary
                fullScreen={false}
                homePath="/"
                title="Page rendering failed"
              >
                <FlakyView />
              </ErrorBoundary>
            }
          />
        </Routes>
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("heading", { name: "Page rendering failed" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Dashboard exploded")).toBeInTheDocument();
    expect(
      container.querySelector('[class*="dark:bg-slate-900/85"]'),
    ).toBeInTheDocument();

    shouldThrow = false;

    await user.click(screen.getByRole("button", { name: "Try again" }));

    expect(screen.getByText("Recovered view")).toBeInTheDocument();
  });
});
