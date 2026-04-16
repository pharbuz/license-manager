import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import type { ApiError } from "../api";
import {
  PageContainer,
  LoadingState,
  ErrorState,
  EmptyState,
} from "../components/common";
import { listAuditLogs } from "../services";
import type {
  AuditLogEntry,
  AuditLogListQuery,
  CollectionPage,
} from "../types";
import { buildCollectionPage } from "../utils/client-pagination";

export function AuditLogsPage() {
  const [search, setSearch] = useState("");
  const [entityType, setEntityType] = useState("");
  const [entityId, setEntityId] = useState("");
  const [page, setPage] = useState(1);

  const serverFilters = useMemo(
    () =>
      ({
        entityType: entityType || undefined,
        entityId: entityId || undefined,
      }) satisfies AuditLogListQuery,
    [entityId, entityType],
  );

  const query = useQuery<AuditLogEntry[], ApiError>({
    queryKey: ["audit-logs", serverFilters],
    queryFn: () => listAuditLogs(serverFilters),
  });

  const pagination: CollectionPage<AuditLogEntry> | undefined = query.data
    ? buildCollectionPage({
        items: query.data,
        search,
        page,
        size: 10,
        searchValues: (entry) => [
          entry.action,
          entry.entityType,
          entry.entityId,
          entry.source,
          entry.summary,
          entry.requestId,
          entry.actorId,
          entry.actorDisplayName,
        ],
      })
    : undefined;

  const items = pagination?.items ?? [];
  const isEmpty = query.isSuccess && pagination?.total === 0;

  return (
    <PageContainer
      title="Audit Logs"
      description="Inspect recorded actions and trace changes across the system."
    >
      <div className="lm-resource-toolbar">
        <label className="lm-resource-toolbar__search">
          <span className="sr-only">Search audit logs</span>
          <input
            value={search}
            onChange={(event) => {
              setSearch(event.target.value);
              setPage(1);
            }}
            placeholder="Search audit logs"
          />
        </label>
        <label className="lm-resource-toolbar__search">
          <span className="sr-only">Entity type</span>
          <input
            value={entityType}
            onChange={(event) => {
              setEntityType(event.target.value);
              setPage(1);
            }}
            placeholder="Filter by entity type"
          />
        </label>
        <label className="lm-resource-toolbar__search">
          <span className="sr-only">Entity ID</span>
          <input
            value={entityId}
            onChange={(event) => {
              setEntityId(event.target.value);
              setPage(1);
            }}
            placeholder="Filter by entity ID"
          />
        </label>
      </div>

      {query.isLoading ? (
        <LoadingState
          title="Loading audit logs"
          description="Fetching the latest recorded events."
        />
      ) : query.isError ? (
        <ErrorState
          title="Unable to load audit logs"
          description={query.error?.message}
        />
      ) : isEmpty ? (
        <EmptyState
          title="No audit events found"
          description="Try broadening the filters."
        />
      ) : (
        <div className="lm-table-wrap">
          <table className="lm-table">
            <thead>
              <tr>
                <th>Occurred</th>
                <th>Action</th>
                <th>Entity</th>
                <th>Source</th>
                <th>Summary</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={item.id}>
                  <td>{new Date(item.occurredAt).toLocaleString()}</td>
                  <td>{item.action}</td>
                  <td>
                    {item.entityType} / {item.entityId}
                  </td>
                  <td>{item.source}</td>
                  <td>{item.summary ?? "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {pagination && pagination.pages > 1 ? (
        <div className="lm-pagination">
          <span>
            Page {pagination.page} of {pagination.pages} · {pagination.total}{" "}
            total
          </span>
          <div className="lm-pagination__actions">
            <button
              type="button"
              className="lm-button"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={pagination.page <= 1}
            >
              Previous
            </button>
            <button
              type="button"
              className="lm-button"
              onClick={() =>
                setPage((current) => Math.min(pagination.pages, current + 1))
              }
              disabled={pagination.page >= pagination.pages}
            >
              Next
            </button>
          </div>
        </div>
      ) : null}
    </PageContainer>
  );
}
