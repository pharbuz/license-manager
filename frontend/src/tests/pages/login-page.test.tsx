import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import { useAuth } from "../../auth";
import { LoginPage } from "../../pages/LoginPage";

vi.mock("../../auth", () => ({
  useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

describe("LoginPage", () => {
  it("renders the sign-in card inside the auth screen shell", () => {
    mockedUseAuth.mockReturnValue({
      isInitialized: true,
      isAuthenticated: false,
      error: null,
      token: null,
      user: null,
      roles: [],
      claims: {},
      login: vi.fn(),
      logout: vi.fn(),
    });

    const { container } = render(
      <MemoryRouter initialEntries={["/login"]}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(
      screen.getByRole("heading", { name: "Sign in to License Manager" }),
    ).toBeInTheDocument();
    expect(container.querySelector(".auth-screen")).toBeInTheDocument();
    expect(container.querySelector(".login-page__card")).toBeInTheDocument();
  });

  it("passes the original route back into the login callback", async () => {
    const user = userEvent.setup();
    const login = vi.fn(async () => undefined);

    mockedUseAuth.mockReturnValue({
      isInitialized: true,
      isAuthenticated: false,
      error: null,
      token: null,
      user: null,
      roles: [],
      claims: {},
      login,
      logout: vi.fn(),
    });

    render(
      <MemoryRouter
        initialEntries={[
          {
            pathname: "/login",
            state: {
              from: {
                pathname: "/licenses",
                search: "?page=2",
                hash: "#active",
              },
            },
          },
        ]}
      >
        <Routes>
          <Route path="/login" element={<LoginPage />} />
        </Routes>
      </MemoryRouter>,
    );

    await user.click(
      screen.getByRole("button", { name: "Continue with Keycloak" }),
    );

    expect(login).toHaveBeenCalledWith("/licenses?page=2#active");
  });
});
