import { describe, expect, it } from "vitest";
import { loadKeycloakConfig, readApiBaseUrl } from "../../config/env";

describe("env config", () => {
  it("loads required Keycloak variables", () => {
    const config = loadKeycloakConfig({
      VITE_KEYCLOAK_URL: "http://localhost:8080",
      VITE_KEYCLOAK_REALM: "license-manager",
      VITE_KEYCLOAK_CLIENT_ID: "license-manager-frontend",
    });

    expect(config).toEqual({
      url: "http://localhost:8080",
      realm: "license-manager",
      clientId: "license-manager-frontend",
    });
  });

  it("throws when required Keycloak variables are missing", () => {
    expect(() =>
      loadKeycloakConfig({
        VITE_KEYCLOAK_URL: "",
        VITE_KEYCLOAK_REALM: "license-manager",
      }),
    ).toThrow("Missing required environment variable: VITE_KEYCLOAK_URL");
  });

  it("uses fallback API base URL", () => {
    expect(readApiBaseUrl({})).toBe("http://localhost:8000");
  });
});
