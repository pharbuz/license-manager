import type { ReactNode } from "react";
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
      <div className="lm-resource-toolbar">
        <label className="lm-resource-toolbar__search">
          <span className="sr-only">Search</span>
          <input
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
            placeholder={searchPlaceholder}
          />
        </label>

        {onCreate ? (
          <button
            type="button"
            className="lm-button lm-button--primary"
            onClick={onCreate}
          >
            {createLabel ?? "Add"}
          </button>
        ) : null}

        {headerActions ? (
          <div className="lm-row-actions">{headerActions}</div>
        ) : null}
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
        <div className="lm-table-wrap">
          <table className="lm-table">
            <thead>
              <tr>
                {columns.map((column) => (
                  <th key={column.header} className={column.className}>
                    {column.header}
                  </th>
                ))}
                {rowActions ? <th>Actions</th> : null}
              </tr>
            </thead>
            <tbody>
              {items.map((item) => (
                <tr key={rowLabel(item)}>
                  {columns.map((column, index) => (
                    <td
                      key={`${rowLabel(item)}-${column.header}-${index}`}
                      className={column.className}
                    >
                      {column.render(item)}
                    </td>
                  ))}
                  {rowActions ? (
                    <td>
                      <div className="lm-row-actions">
                        {rowActions.map((action) => (
                          <button
                            key={action.label}
                            type="button"
                            className={
                              action.tone === "danger"
                                ? "lm-button lm-button--danger"
                                : "lm-button"
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
      )}

      {page !== undefined &&
      pages !== undefined &&
      total !== undefined &&
      pages > 1 &&
      onPageChange ? (
        <div className="lm-pagination">
          <span>
            Page {page} of {pages} · {total} total
          </span>
          <div className="lm-pagination__actions">
            <button
              type="button"
              className="lm-button"
              onClick={() => onPageChange(Math.max(1, page - 1))}
              disabled={page <= 1}
            >
              Previous
            </button>
            <button
              type="button"
              className="lm-button"
              onClick={() => onPageChange(Math.min(pages, page + 1))}
              disabled={page >= pages}
            >
              Next
            </button>
          </div>
        </div>
      ) : null}

      {children}
    </PageContainer>
  );
}
