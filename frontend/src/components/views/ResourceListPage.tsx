import type { ReactNode } from "react";
import { ChevronLeft, ChevronRight, Plus, Search } from "lucide-react";
import { EmptyState, ErrorState, LoadingState, PageContainer } from "../common";

export type ResourceColumn<TItem> = {
  header: string;
  render: (item: TItem) => ReactNode;
  className?: string;
};

export type ResourceAction<TItem> = {
  label: string;
  onClick: (item: TItem) => void;
  tone?: "default" | "danger";
};

type ResourceListPageProps<TItem> = {
  title: string;
  description: string;
  search: string;
  searchPlaceholder?: string;
  onSearchChange: (value: string) => void;
  createLabel?: string;
  onCreate?: () => void;
  headerActions?: ReactNode;
  columns: Array<ResourceColumn<TItem>>;
  items: TItem[];
  rowLabel: (item: TItem) => string;
  rowActions?: Array<ResourceAction<TItem>>;
  isLoading?: boolean;
  isError?: boolean;
  errorMessage?: string;
  isEmpty?: boolean;
  emptyTitle?: string;
  emptyDescription?: string;
  page?: number;
  pages?: number;
  total?: number;
  onPageChange?: (nextPage: number) => void;
  children?: ReactNode;
};

export function ResourceListPage<TItem>({
  title,
  description,
  search,
  searchPlaceholder = "Search",
  onSearchChange,
  createLabel,
  onCreate,
  headerActions,
  columns,
  items,
  rowLabel,
  rowActions,
  isLoading,
  isError,
  errorMessage,
  isEmpty,
  emptyTitle,
  emptyDescription,
  page,
  pages,
  total,
  onPageChange,
  children,
}: ResourceListPageProps<TItem>) {
  return (
    <PageContainer title={title} description={description}>
      <div className="rounded-[28px] border border-slate-200 bg-white/90 p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900/80">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <label className="relative block w-full max-w-xl">
            <span className="sr-only">Search</span>
            <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              value={search}
              onChange={(event) => onSearchChange(event.target.value)}
              placeholder={searchPlaceholder}
              className="h-12 w-full rounded-2xl border border-slate-200 bg-slate-50 pl-11 pr-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-400 focus:bg-white focus:ring-4 focus:ring-blue-500/10 dark:border-slate-700 dark:bg-slate-950 dark:text-white dark:placeholder:text-slate-500 dark:focus:border-blue-500 dark:focus:bg-slate-900"
            />
          </label>

          <div className="flex flex-wrap items-center gap-3">
            {headerActions ? (
              <div className="flex flex-wrap items-center gap-3">
                {headerActions}
              </div>
            ) : null}

            {onCreate ? (
              <button
                type="button"
                className="inline-flex items-center gap-2 rounded-2xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-500/20"
                onClick={onCreate}
              >
                <Plus className="h-4 w-4" />
                <span>{createLabel ?? "Add"}</span>
              </button>
            ) : null}
          </div>
        </div>
      </div>

      {isLoading ? (
        <LoadingState
          title="Loading records"
          description="Fetching the latest data from the API."
        />
      ) : isError ? (
        <ErrorState
          title="Unable to load records"
          description={errorMessage ?? "Please try again."}
        />
      ) : isEmpty ? (
        <EmptyState title={emptyTitle} description={emptyDescription} />
      ) : (
        <div className="overflow-hidden rounded-[28px] border border-slate-200 bg-white/95 shadow-sm dark:border-slate-800 dark:bg-slate-900/85">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-800">
              <thead className="bg-slate-50 dark:bg-slate-950/60">
                <tr>
                  {columns.map((column) => (
                    <th
                      key={column.header}
                      className={`px-5 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400 ${column.className ?? ""}`}
                    >
                      {column.header}
                    </th>
                  ))}
                  {rowActions ? (
                    <th className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-[0.18em] text-slate-500 dark:text-slate-400">
                      Actions
                    </th>
                  ) : null}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800/80">
                {items.map((item) => (
                  <tr
                    key={rowLabel(item)}
                    className="align-top transition hover:bg-slate-50/80 dark:hover:bg-slate-800/40"
                  >
                    {columns.map((column, index) => (
                      <td
                        key={`${rowLabel(item)}-${column.header}-${index}`}
                        className={`px-5 py-4 text-sm text-slate-700 dark:text-slate-200 ${column.className ?? ""}`}
                      >
                        {column.render(item)}
                      </td>
                    ))}
                    {rowActions ? (
                      <td className="px-5 py-4">
                        <div className="flex flex-wrap gap-2">
                          {rowActions.map((action) => (
                            <button
                              key={action.label}
                              type="button"
                              className={
                                action.tone === "danger"
                                  ? "rounded-xl border border-red-200 px-3 py-1.5 text-sm font-medium text-red-600 transition hover:bg-red-50 dark:border-red-950 dark:text-red-400 dark:hover:bg-red-950/30"
                                  : "rounded-xl border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
                              }
                              onClick={() => action.onClick(item)}
                            >
                              {action.label}
                            </button>
                          ))}
                        </div>
                      </td>
                    ) : null}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {page !== undefined &&
      pages !== undefined &&
      total !== undefined &&
      pages > 1 &&
      onPageChange ? (
        <div className="flex flex-col gap-3 rounded-[28px] border border-slate-200 bg-white/90 px-5 py-4 shadow-sm sm:flex-row sm:items-center sm:justify-between dark:border-slate-800 dark:bg-slate-900/80">
          <span className="text-sm text-slate-500 dark:text-slate-400">
            Page {page} of {pages} · {total} total
          </span>
          <div className="flex items-center gap-2">
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              onClick={() => onPageChange(Math.max(1, page - 1))}
              disabled={page <= 1}
            >
              <ChevronLeft className="h-4 w-4" />
              Previous
            </button>
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
              onClick={() => onPageChange(Math.min(pages, page + 1))}
              disabled={page >= pages}
            >
              Next
              <ChevronRight className="h-4 w-4" />
            </button>
          </div>
        </div>
      ) : null}

      {children}
    </PageContainer>
  );
}
