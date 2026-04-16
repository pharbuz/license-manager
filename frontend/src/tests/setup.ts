import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, vi } from "vitest";
import { MockKeycloak, resetKeycloakMock } from "./mocks/keycloak";

vi.mock("keycloak-js", () => ({
  default: MockKeycloak,
}));

beforeEach(() => {
  resetKeycloakMock();
  vi.stubEnv("VITE_KEYCLOAK_URL", "http://localhost:8080");
  vi.stubEnv("VITE_KEYCLOAK_REALM", "license-manager");
  vi.stubEnv("VITE_KEYCLOAK_CLIENT_ID", "license-manager-frontend");
});

afterEach(() => {
  vi.unstubAllEnvs();
});
