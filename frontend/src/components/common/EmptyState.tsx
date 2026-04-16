import { Inbox } from "lucide-react";

type EmptyStateProps = {
  title?: string;
  description?: string;
};

export function EmptyState({
  title = "No data yet",
  description = "Create your first record to populate this view.",
}: EmptyStateProps) {
  return (
    <div
      className="flex min-h-72 flex-col items-center justify-center rounded-[28px] border border-dashed border-slate-300 bg-white/75 px-6 py-10 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900/60"
      role="status"
      aria-live="polite"
    >
      <span className="flex h-14 w-14 items-center justify-center rounded-full bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-300">
        <Inbox className="h-6 w-6" aria-hidden="true" />
      </span>
      <h2 className="mt-4 text-lg font-semibold text-slate-950 dark:text-white">
        {title}
      </h2>
      <p className="mt-2 max-w-md text-sm text-slate-500 dark:text-slate-400">
        {description}
      </p>
    </div>
  );
}
