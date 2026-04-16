import {
  Activity,
  Archive,
  Boxes,
  Building2,
  Database,
  FileClock,
  PackageSearch,
  RefreshCw,
  ShieldCheck,
  TriangleAlert,
} from "lucide-react";
import { ErrorState, LoadingState, PageContainer } from "../components/common";
import { useDashboardOverview } from "../hooks/use-dashboard-overview";

function formatDateTime(value: string): string {
  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export function DashboardPage() {
  const overviewQuery = useDashboardOverview();

  if (overviewQuery.isLoading) {
    return (
      <PageContainer
        title="Dashboard"
        description="Operational snapshot of platform health and business workloads."
      >
        <LoadingState
          title="Building operational snapshot"
          description="Collecting health and workload signals from License Manager services."
        />
      </PageContainer>
    );
  }

  if (overviewQuery.isError || !overviewQuery.data) {
    return (
      <PageContainer
        title="Dashboard"
        description="Operational snapshot of platform health and business workloads."
      >
        <ErrorState
          title="Unable to load dashboard"
          description={
            overviewQuery.error?.message ??
            "Dashboard data could not be fetched from the API."
          }
        />
      </PageContainer>
    );
  }

  const { data } = overviewQuery;
  const statusLabel = data.health.status === "ok" ? "Healthy" : "Degraded";

  const metricCards = [
    {
      id: "active-licenses",
      label: "Active licenses",
      value: data.metrics.activeLicenses,
      description: "Licenses currently in active inventory.",
      icon: ShieldCheck,
    },
    {
      id: "expiring-soon",
      label: "Expiring in 30 days",
      value: data.metrics.expiringSoonLicenses,
      description: "Active licenses nearing expiration.",
      icon: FileClock,
    },
    {
      id: "expired",
      label: "Expired licenses",
      value: data.metrics.expiredLicenses,
      description: "Licenses that passed the end date.",
      icon: TriangleAlert,
    },
    {
      id: "archived-licenses",
      label: "Archived licenses",
      value: data.metrics.archivedLicenses,
      description: "Records moved out of active inventory.",
      icon: Archive,
    },
    {
      id: "customers",
      label: "Customers",
      value: data.metrics.customers,
      description: "Total customer accounts available.",
      icon: Building2,
    },
    {
      id: "products",
      label: "Products",
      value: data.metrics.products,
      description: "Products connected to licensing.",
      icon: Boxes,
    },
    {
      id: "app-packages",
      label: "App packages",
      value: data.metrics.appPackages,
      description: "Deployable package versions tracked.",
      icon: PackageSearch,
    },
    {
      id: "audit-events",
      label: "Audit events",
      value: data.metrics.auditEvents,
      description: "Events currently returned by /audit/logs.",
      icon: Database,
    },
  ];

  return (
    <PageContainer
      title="Dashboard"
      description="Operational snapshot of platform health and business workloads."
      actions={
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
          onClick={() => overviewQuery.refetch()}
          disabled={overviewQuery.isFetching}
        >
          <RefreshCw
            className={`h-4 w-4 ${overviewQuery.isFetching ? "animate-spin" : ""}`}
          />
          {overviewQuery.isFetching ? "Refreshing..." : "Refresh"}
        </button>
      }
    >
      <section
        className="grid gap-4 xl:grid-cols-[1.4fr_1fr]"
        aria-label="Health summary"
      >
        <article className="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">
                Platform health
              </p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950 dark:text-white">
                System status: {statusLabel}
              </h2>
              <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
                Runtime readiness across storage and secret management services.
              </p>
            </div>

            <span
              className={`inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-semibold ${
                data.health.status === "ok"
                  ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300"
                  : "bg-amber-100 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300"
              }`}
            >
              <Activity className="h-4 w-4" />
              {statusLabel}
            </span>
          </div>
        </article>

        <ul className="grid gap-3 sm:grid-cols-2">
          {data.serviceStates.map((service) => (
            <li
              key={service.name}
              className="rounded-[24px] border border-slate-200 bg-white/95 p-5 shadow-sm dark:border-slate-800 dark:bg-slate-900/85"
            >
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-semibold text-slate-900 dark:text-white">
                    {service.name}
                  </p>
                  <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
                    {service.status === "ok" ? "Operational" : "Error"}
                  </p>
                </div>
                <span
                  className={`h-3 w-3 rounded-full ${
                    service.status === "ok" ? "bg-emerald-500" : "bg-red-500"
                  }`}
                  aria-hidden="true"
                />
              </div>
            </li>
          ))}
        </ul>
      </section>

      <section
        className="grid gap-4 md:grid-cols-2 xl:grid-cols-4"
        aria-label="Operational metrics"
      >
        {metricCards.map((card) => (
          <article
            key={card.id}
            className="rounded-[28px] border border-slate-200 bg-white/95 p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md dark:border-slate-800 dark:bg-slate-900/85"
            data-testid={`metric-${card.id}`}
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-medium text-slate-500 dark:text-slate-400">
                  {card.label}
                </p>
                <strong className="mt-3 block text-3xl font-bold tracking-tight text-slate-950 dark:text-white">
                  {card.value}
                </strong>
              </div>
              <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-50 text-blue-600 dark:bg-blue-950/60 dark:text-blue-300">
                <card.icon className="h-5 w-5" />
              </span>
            </div>
            <p className="mt-4 text-sm text-slate-500 dark:text-slate-400">
              {card.description}
            </p>
          </article>
        ))}
      </section>

      <section
        className="grid gap-4 lg:grid-cols-3"
        aria-label="Operational insights"
      >
        <article className="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
          <h3 className="text-base font-semibold text-slate-950 dark:text-white">
            Latest audit event
          </h3>
          <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
            {data.latestAuditAt
              ? formatDateTime(data.latestAuditAt)
              : "No audit events returned by the API."}
          </p>
        </article>

        <article className="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
          <h3 className="text-base font-semibold text-slate-950 dark:text-white">
            Attention needed
          </h3>
          {data.attention.length > 0 ? (
            <ul className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
              {data.attention.map((item) => (
                <li
                  key={item}
                  className="rounded-2xl bg-amber-50 px-3 py-2 dark:bg-amber-950/30"
                >
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
              No immediate operational risks detected.
            </p>
          )}
        </article>

        <article className="rounded-[28px] border border-slate-200 bg-white/95 p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
          <h3 className="text-base font-semibold text-slate-950 dark:text-white">
            Snapshot refreshed
          </h3>
          <p className="mt-3 text-sm text-slate-500 dark:text-slate-400">
            {formatDateTime(data.refreshedAt)}
          </p>
        </article>
      </section>
    </PageContainer>
  );
}
