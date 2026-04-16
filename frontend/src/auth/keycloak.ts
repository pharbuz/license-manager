import Keycloak from "keycloak-js";
import { loadKeycloakConfig } from "../config/env";

let keycloakInstance: Keycloak | null = null;
let keycloakInitPromise: Promise<boolean> | null = null;

export function getKeycloak(): Keycloak {
  if (!keycloakInstance) {
    const { url, realm, clientId } = loadKeycloakConfig();
    keycloakInstance = new Keycloak({
      url,
      realm,
      clientId,
    });
  }

  return keycloakInstance;
}

export async function initKeycloak(
  options: Parameters<Keycloak["init"]>[0],
): Promise<boolean> {
  const keycloak = getKeycloak();

  if (!keycloakInitPromise) {
    keycloakInitPromise = keycloak.init(options).catch((error) => {
      keycloakInitPromise = null;
      throw error;
    });
  }

  return keycloakInitPromise;
}

export function resetKeycloakForTests() {
  keycloakInstance = null;
  keycloakInitPromise = null;
}
