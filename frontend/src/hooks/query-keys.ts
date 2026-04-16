import type { ListQueryParams, Uuid } from "../types";

export const queryKeys = {
  dashboard: {
    all: ["dashboard"] as const,
    overview: () => [...queryKeys.dashboard.all, "overview"] as const,
  },
  dropdowns: {
    all: ["dropdowns"] as const,
    list: (type: string) => [...queryKeys.dropdowns.all, "list", type] as const,
  },
  customers: {
    all: ["customers"] as const,
    list: (params?: ListQueryParams) =>
      [...queryKeys.customers.all, "list", params ?? {}] as const,
    detail: (customerId: Uuid) =>
      [...queryKeys.customers.all, "detail", customerId] as const,
  },
  products: {
    all: ["products"] as const,
    list: (params?: ListQueryParams) =>
      [...queryKeys.products.all, "list", params ?? {}] as const,
    detail: (productId: Uuid) =>
      [...queryKeys.products.all, "detail", productId] as const,
  },
  kinds: {
    all: ["kinds"] as const,
    list: (params?: ListQueryParams) =>
      [...queryKeys.kinds.all, "list", params ?? {}] as const,
    detail: (kindId: Uuid) =>
      [...queryKeys.kinds.all, "detail", kindId] as const,
  },
  licenses: {
    all: ["licenses"] as const,
    list: (params?: ListQueryParams) =>
      [...queryKeys.licenses.all, "list", params ?? {}] as const,
    archived: (params?: ListQueryParams) =>
      [...queryKeys.licenses.all, "archived", params ?? {}] as const,
    byCustomer: (customerId: Uuid, params?: ListQueryParams) =>
      [
        ...queryKeys.licenses.all,
        "by-customer",
        customerId,
        params ?? {},
      ] as const,
    detail: (licenseId: Uuid) =>
      [...queryKeys.licenses.all, "detail", licenseId] as const,
  },
  appPackages: {
    all: ["app-packages"] as const,
    list: (params?: ListQueryParams) =>
      [...queryKeys.appPackages.all, "list", params ?? {}] as const,
    detail: (appPackageId: Uuid) =>
      [...queryKeys.appPackages.all, "detail", appPackageId] as const,
  },
  smtpCredentials: {
    all: ["smtp-credentials"] as const,
    current: () => [...queryKeys.smtpCredentials.all, "current"] as const,
  },
  auditLogs: {
    all: ["audit-logs"] as const,
    list: (params?: Record<string, unknown>) =>
      [...queryKeys.auditLogs.all, "list", params ?? {}] as const,
  },
  health: {
    all: ["health"] as const,
    status: () => [...queryKeys.health.all, "status"] as const,
  },
};
