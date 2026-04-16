import { useQuery } from "@tanstack/react-query";
import type { ApiError } from "../api";
import {
  getHealth,
  listAppPackages,
  listArchivedLicenses,
  listAuditLogs,
  listCustomers,
  listLicenses,
  listProducts,
} from "../services";
import type { HealthResponse } from "../types";
import { queryKeys } from "./query-keys";

export type DashboardOverview = {
  health: HealthResponse;
  metrics: {
    activeLicenses: number;
    archivedLicenses: number;
    expiringSoonLicenses: number;
    expiredLicenses: number;
    customers: number;
    products: number;
    appPackages: number;
    auditEvents: number;
  };
  serviceStates: Array<{
    name: string;
    status: "ok" | "error";
  }>;
  attention: string[];
  latestAuditAt: string | null;
  refreshedAt: string;
};

const DAY_IN_MS = 24 * 60 * 60 * 1000;

export function useDashboardOverview() {
  return useQuery<DashboardOverview, ApiError>({
    queryKey: queryKeys.dashboard.overview(),
    queryFn: async () => {
      const [
        health,
        licenses,
        archived,
        customers,
        products,
        appPackages,
        auditLogs,
      ] = await Promise.all([
        getHealth(),
        listLicenses(),
        listArchivedLicenses(),
        listCustomers(),
        listProducts(),
        listAppPackages(),
        listAuditLogs(),
      ]);

      const now = new Date();
      const expiringLimit = new Date(now.getTime() + 30 * DAY_IN_MS);

      const expiredLicenses = licenses.filter(
        (license) => new Date(license.endDate) < now,
      ).length;

      const expiringSoonLicenses = licenses.filter((license) => {
        const endDate = new Date(license.endDate);
        return endDate >= now && endDate <= expiringLimit;
      }).length;

      const serviceStates = [
        { name: "PostgreSQL", status: health.services.postgres },
        { name: "Key Vault", status: health.services.keyVault },
      ] as const;

      const attention: string[] = [];

      if (health.status !== "ok") {
        attention.push("One or more infrastructure dependencies are degraded.");
      }

      if (expiredLicenses > 0) {
        attention.push(`${expiredLicenses} active license(s) already expired.`);
      }

      if (expiringSoonLicenses > 0) {
        attention.push(
          `${expiringSoonLicenses} license(s) will expire within the next 30 days.`,
        );
      }

      const latestAuditAt =
        auditLogs
          .map((item) => item.occurredAt)
          .sort(
            (left, right) =>
              new Date(right).getTime() - new Date(left).getTime(),
          )[0] ?? null;

      return {
        health,
        metrics: {
          activeLicenses: licenses.length,
          archivedLicenses: archived.length,
          expiringSoonLicenses,
          expiredLicenses,
          customers: customers.length,
          products: products.length,
          appPackages: appPackages.length,
          auditEvents: auditLogs.length,
        },
        serviceStates: [...serviceStates],
        attention,
        latestAuditAt,
        refreshedAt: now.toISOString(),
      };
    },
  });
}
