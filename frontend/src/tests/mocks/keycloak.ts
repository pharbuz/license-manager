import { vi } from "vitest";
import type { KeycloakTokenParsed } from "keycloak-js";

export const keycloakMock = {
  authenticated: true,
  token: "test-access-token",
  tokenParsed: {
    sub: "user-1",
    preferred_username: "test.user",
    name: "Test User",
    email: "test@example.com",
    realm_access: { roles: ["user"] },
    resource_access: {
      "license-manager-frontend": {
        roles: ["viewer"],
      },
    },
  } as KeycloakTokenParsed,
  clientId: "license-manager-frontend",
  init: vi.fn(async () => true),
  login: vi.fn(async () => undefined),
  logout: vi.fn(async () => undefined),
  updateToken: vi.fn(async () => true),
  clearToken: vi.fn(),
  onAuthSuccess: undefined,
  onAuthError: undefined,
  onAuthRefreshSuccess: undefined,
  onAuthRefreshError: undefined,
  onAuthLogout: undefined,
  onTokenExpired: undefined,
};

export class MockKeycloak {
  constructor() {
    return keycloakMock as unknown as MockKeycloak;
  }
}

export function resetKeycloakMock() {
  keycloakMock.authenticated = true;
  keycloakMock.token = "test-access-token";
  keycloakMock.tokenParsed = {
    sub: "user-1",
    preferred_username: "test.user",
    name: "Test User",
    email: "test@example.com",
    realm_access: { roles: ["user"] },
    resource_access: {
      "license-manager-frontend": {
        roles: ["viewer"],
      },
    },
  } as KeycloakTokenParsed;

  keycloakMock.init.mockReset();
  keycloakMock.init.mockResolvedValue(true);

  keycloakMock.login.mockReset();
  keycloakMock.login.mockResolvedValue(undefined);

  keycloakMock.logout.mockReset();
  keycloakMock.logout.mockResolvedValue(undefined);

  keycloakMock.updateToken.mockReset();
  keycloakMock.updateToken.mockResolvedValue(true);

  keycloakMock.clearToken.mockReset();

  keycloakMock.onAuthSuccess = undefined;
  keycloakMock.onAuthError = undefined;
  keycloakMock.onAuthRefreshSuccess = undefined;
  keycloakMock.onAuthRefreshError = undefined;
  keycloakMock.onAuthLogout = undefined;
  keycloakMock.onTokenExpired = undefined;
}
