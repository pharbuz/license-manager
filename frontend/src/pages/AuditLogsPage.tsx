import { useQuery } from "@tanstack/react-query";
import { ChevronLeft, ChevronRight, Search } from "lucide-react";
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
      <div className="rounded-[28px] border border-slate-200 bg-white/90 p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900/80">
        <div className="grid gap-3 lg:grid-cols-3">
          {[
            {
              label: "Search audit logs",
              value: search,
              placeholder: "Search audit logs",
              onChange: (value: string) => {
                setSearch(value);
                setPage(1);
              },
            },
            {
              label: "Entity type",
              value: entityType,
              placeholder: "Filter by entity type",
              onChange: (value: string) => {
                setEntityType(value);
                setPage(1);
              },
            },
            {
              label: "Entity ID",
              value: entityId,
              placeholder: "Filter by entity ID",
              onChange: (value: string) => {
                setEntityId(value);
                setPage(1);
              },
            },
          ].map((field) => (
            <label key={field.label} className="relative block">
              <span className="sr-only">{field.label}</span>
              <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
              <input
                value={field.value}
                onChange={(event) => field.onChange(event.target.value)}
                placeholder={field.placeholder}
                className="h-12 w-full rounded-2xl border border-slate-200 bg-slate-50 pl-11 pr-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-500/10 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:placeholder:text-slate-500 dark:focus:border-blue-500 dark:focus:bg-slate-900"
              />
            </label>
          ))}
        </div>
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
        <div className="overflow-hidden rounded-[28px] border border-slate-200 bg-white/95 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
              <thead className="bg-slate-50 dark:bg-slate-950/60">
                <tr>
                  {["Occurred", "Action", "Entity", "Source", "Summary"].map(
                    (header) => (
                      <th
                        key={header}
                        className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400"
                      >
                        {header}
                      </th>
                    ),
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
                {items.map((item) => (
                  <tr
                    key={item.id}
                    className="transition hover:bg-slate-50/80 dark:hover:bg-slate-800/40"
                  >
                    <td className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">
                      {new Date(item.occurredAt).toLocaleString()}
                    </td>
                    <td className="px-5 py-4 text-sm font-medium text-slate-900 dark:text-white">
                      {item.action}
                    </td>
                    <td className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">
                      {item.entityType} / {item.entityId}
                    </td>
                    <td className="px-5 py-4 text-sm text-slate-700 dark:text-slate-200">
                      {item.source}
                    </td>
                    <td className="px-5 py-4 text-sm text-slate-500 dark:text-slate-400">
                      {item.summary ?? "-"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {pagination && pagination.pages > 1 ? (
        <div className="flex flex-col gap-3 rounded-[28px] border border-slate-200 bg-white/90 px-5 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between dark:border-slate-800 dark:bg-slate-900/80">
          <span className="text-sm text-slate-500 dark:text-slate-400">
            Page {pagination.page} of {pagination.pages} · {pagination.total}{" "}
            total
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={pagination.page <= 1}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </button>
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              onClick={() =>
                setPage((current) => Math.min(pagination.pages, current + 1))
              }
              disabled={pagination.page >= pagination.pages}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      ) : null}
    </PageContainer>
  );
}
