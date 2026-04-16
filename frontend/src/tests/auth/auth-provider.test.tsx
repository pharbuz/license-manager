import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it } from "vitest";
import { AppProviders } from "../../app/providers";
import { resetKeycloakForTests } from "../../auth/keycloak";
import { keycloakMock } from "../mocks/keycloak";

describe("AuthProvider", () => {
  beforeEach(() => {
    resetKeycloakForTests();
  });

  it("applies dark mode before showing the initializing authentication screen", () => {
    window.localStorage.setItem("darkMode", "true");
    keycloakMock.init.mockImplementation(() => new Promise(() => undefined));

    const { container } = render(
      <AppProviders>
        <div>Application content</div>
      </AppProviders>,
    );

    expect(
      screen.getByRole("heading", { name: "Initializing authentication" }),
    ).toBeInTheDocument();
    expect(document.documentElement).toHaveClass("dark");
    expect(container.querySelector(".auth-screen")).toBeInTheDocument();
  });
});
