import type Keycloak from "keycloak-js";

let keycloakClient: Keycloak | null = null;
let refreshInFlight: Promise<void> | null = null;
let authFailureHandler: (() => void) | null = null;

export function setAuthClient(client: Keycloak | null) {
  keycloakClient = client;
  if (!client) {
    refreshInFlight = null;
  }
}

export function setAuthFailureHandler(handler: (() => void) | null) {
  authFailureHandler = handler;
}

export function getAccessToken(): string | null {
  if (!keycloakClient?.authenticated || !keycloakClient.token) {
    return null;
  }

  return keycloakClient.token;
}

function hasRefreshToken(client: Keycloak): boolean {
  return (
    typeof client.refreshToken === "string" && client.refreshToken.length > 0
  );
}

export async function ensureFreshToken(
  minValidity = 30,
): Promise<string | null> {
  if (!keycloakClient?.authenticated || !keycloakClient.token) {
    return null;
  }

  if (!hasRefreshToken(keycloakClient)) {
    if (!keycloakClient.isTokenExpired(0)) {
      return keycloakClient.token;
    }

    authFailureHandler?.();
    return null;
  }

  if (!refreshInFlight) {
    refreshInFlight = keycloakClient
      .updateToken(minValidity)
      .then(() => undefined)
      .finally(() => {
        refreshInFlight = null;
      });
  }

  try {
    await refreshInFlight;
  } catch (error) {
    authFailureHandler?.();
    throw error;
  }

  if (!keycloakClient.authenticated || !keycloakClient.token) {
    return null;
  }

  return keycloakClient.token;
}

export function resetAuthSessionForTests() {
  keycloakClient = null;
  refreshInFlight = null;
  authFailureHandler = null;
}
