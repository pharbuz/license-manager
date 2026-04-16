import "@testing-library/jest-dom/vitest";
import { afterEach, beforeEach, vi } from "vitest";
import { MockKeycloak, resetKeycloakMock } from "./mocks/keycloak";

vi.mock("keycloak-js", () => ({
  default: MockKeycloak,
}));

function ensureLocalStorage(): Storage {
  const storage = window.localStorage as Partial<Storage> | undefined;
  if (
    storage &&
    typeof storage.getItem === "function" &&
    typeof storage.setItem === "function" &&
    typeof storage.removeItem === "function"
  ) {
    return storage as Storage;
  }

  const values = new Map<string, string>();
  const localStorageMock: Storage = {
    get length() {
      return values.size;
    },
    clear() {
      values.clear();
    },
    getItem(key) {
      return values.get(key) ?? null;
    },
    key(index) {
      return Array.from(values.keys())[index] ?? null;
    },
    removeItem(key) {
      values.delete(key);
    },
    setItem(key, value) {
      values.set(key, String(value));
    },
  };

  Object.defineProperty(window, "localStorage", {
    configurable: true,
    value: localStorageMock,
  });

  return localStorageMock;
}

function resetThemeStorage() {
  ensureLocalStorage().removeItem("darkMode");
}

beforeEach(() => {
  resetKeycloakMock();
  ensureLocalStorage();
  resetThemeStorage();
  document.documentElement.classList.remove("dark");
  vi.stubEnv("VITE_KEYCLOAK_URL", "http://localhost:8080");
  vi.stubEnv("VITE_KEYCLOAK_REALM", "license-manager");
  vi.stubEnv("VITE_KEYCLOAK_CLIENT_ID", "license-manager-frontend");
});

afterEach(() => {
  resetThemeStorage();
  document.documentElement.classList.remove("dark");
  vi.unstubAllEnvs();
});
