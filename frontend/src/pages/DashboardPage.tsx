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
    },
    {
      id: "expiring-soon",
      label: "Expiring in 30 days",
      value: data.metrics.expiringSoonLicenses,
      description: "Active licenses nearing expiration.",
    },
    {
      id: "expired",
      label: "Expired licenses",
      value: data.metrics.expiredLicenses,
      description: "Licenses that passed the end date.",
    },
    {
      id: "archived-licenses",
      label: "Archived licenses",
      value: data.metrics.archivedLicenses,
      description: "Records moved out of active inventory.",
    },
    {
      id: "customers",
      label: "Customers",
      value: data.metrics.customers,
      description: "Total customer accounts available.",
    },
    {
      id: "products",
      label: "Products",
      value: data.metrics.products,
      description: "Products connected to licensing.",
    },
    {
      id: "app-packages",
      label: "App packages",
      value: data.metrics.appPackages,
      description: "Deployable package versions tracked.",
    },
    {
      id: "audit-events",
      label: "Audit events",
      value: data.metrics.auditEvents,
      description: "Events currently returned by /audit/logs.",
    },
  ];

  return (
    <PageContainer
      title="Dashboard"
      description="Operational snapshot of platform health and business workloads."
      actions={
        <button
          type="button"
          className="lm-button"
          onClick={() => overviewQuery.refetch()}
          disabled={overviewQuery.isFetching}
        >
          {overviewQuery.isFetching ? "Refreshing..." : "Refresh"}
        </button>
      }
    >
      <section className="lm-dashboard-health" aria-label="Health summary">
        <div>
          <h2>System status: {statusLabel}</h2>
          <p>Live signal from the `/health` endpoint.</p>
        </div>

        <ul className="lm-dashboard-service-list">
          {data.serviceStates.map((service) => (
            <li key={service.name}>
              <span
                className={`lm-dashboard-service-dot lm-dashboard-service-dot--${service.status}`}
                aria-hidden="true"
              />
              <strong>{service.name}</strong>
              <span>{service.status === "ok" ? "Operational" : "Error"}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="lm-dashboard-grid" aria-label="Operational metrics">
        {metricCards.map((card) => (
          <article
            key={card.id}
            className="lm-dashboard-card"
            data-testid={`metric-${card.id}`}
          >
            <h3>{card.label}</h3>
            <strong>{card.value}</strong>
            <p>{card.description}</p>
          </article>
        ))}
      </section>

      <section
        className="lm-dashboard-details"
        aria-label="Operational insights"
      >
        <article className="lm-dashboard-card">
          <h3>Latest audit event</h3>
          <p>
            {data.latestAuditAt
              ? formatDateTime(data.latestAuditAt)
              : "No audit events returned by the API."}
          </p>
        </article>

        <article className="lm-dashboard-card">
          <h3>Attention needed</h3>
          {data.attention.length > 0 ? (
            <ul className="lm-dashboard-attention-list">
              {data.attention.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          ) : (
            <p>No immediate operational risks detected.</p>
          )}
        </article>

        <article className="lm-dashboard-card">
          <h3>Snapshot refreshed</h3>
          <p>{formatDateTime(data.refreshedAt)}</p>
        </article>
      </section>
    </PageContainer>
  );
}
