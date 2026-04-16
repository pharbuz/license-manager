export type KeycloakConfig = {
  url: string;
  realm: string;
  clientId: string;
};

type EnvSource = Record<string, string | undefined>;

const DEFAULT_API_BASE_URL = "http://localhost:8000";

function readEnvValue(source: EnvSource, key: string): string | undefined {
  const value = source[key];
  if (!value) {
    return undefined;
  }

  const trimmedValue = value.trim();
  return trimmedValue.length > 0 ? trimmedValue : undefined;
}

function readRequiredEnv(source: EnvSource, key: string): string {
  const value = readEnvValue(source, key);

  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`);
  }

  return value;
}

export function loadKeycloakConfig(
  source: EnvSource = import.meta.env,
): KeycloakConfig {
  return {
    url: readRequiredEnv(source, "VITE_KEYCLOAK_URL"),
    realm: readRequiredEnv(source, "VITE_KEYCLOAK_REALM"),
    clientId: readRequiredEnv(source, "VITE_KEYCLOAK_CLIENT_ID"),
  };
}

export function readApiBaseUrl(source: EnvSource = import.meta.env): string {
  return readEnvValue(source, "VITE_API_BASE_URL") ?? DEFAULT_API_BASE_URL;
}
