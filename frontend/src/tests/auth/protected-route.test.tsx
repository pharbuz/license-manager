import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { ProtectedRoute } from "../../components/auth/ProtectedRoute";
import { useAuth } from "../../auth";

vi.mock("../../auth", () => ({
  useAuth: vi.fn(),
}));

const mockedUseAuth = vi.mocked(useAuth);

describe("ProtectedRoute", () => {
  it("shows loading state while auth is initializing", () => {
    mockedUseAuth.mockReturnValue({
      isInitialized: false,
      isAuthenticated: false,
      error: null,
      token: null,
      user: null,
      roles: [],
      claims: {},
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<div>Private content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("Loading application")).toBeInTheDocument();
  });

  it("redirects anonymous users to login route", () => {
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

    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/login" element={<div>Login</div>} />
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<div>Private content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("Login")).toBeInTheDocument();
  });

  it("renders protected outlet when authenticated", () => {
    mockedUseAuth.mockReturnValue({
      isInitialized: true,
      isAuthenticated: true,
      error: null,
      token: "token",
      user: {
        id: "user-1",
        username: "test.user",
        name: "Test User",
        email: "test@example.com",
      },
      roles: ["user"],
      claims: {},
      login: vi.fn(),
      logout: vi.fn(),
    });

    render(
      <MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route element={<ProtectedRoute />}>
            <Route path="/" element={<div>Private content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText("Private content")).toBeInTheDocument();
  });
});
