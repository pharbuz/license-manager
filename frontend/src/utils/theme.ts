const DARK_MODE_STORAGE_KEY = "darkMode";

function getStorage(): Storage | null {
  if (typeof window === "undefined") {
    return null;
  }

  const storage = window.localStorage;
  if (!storage || typeof storage.getItem !== "function") {
    return null;
  }

  return storage;
}

export function readStoredDarkMode(): boolean {
  if (typeof document === "undefined") {
    return false;
  }

  const storage = getStorage();
  const saved = storage?.getItem(DARK_MODE_STORAGE_KEY);

  if (saved === null || saved === undefined) {
    return document.documentElement.classList.contains("dark");
  }

  return saved === "true";
}

export function applyDarkModeClass(isDark: boolean) {
  if (typeof document === "undefined") {
    return;
  }

  document.documentElement.classList.toggle("dark", isDark);
}

export function persistDarkMode(isDark: boolean) {
  const storage = getStorage();
  if (!storage || typeof storage.setItem !== "function") {
    return;
  }

  storage.setItem(DARK_MODE_STORAGE_KEY, String(isDark));
}

export function initializeTheme(): boolean {
  const isDark = readStoredDarkMode();
  applyDarkModeClass(isDark);
  return isDark;
}
