import { TriangleAlert } from "lucide-react";

type ErrorStateProps = {
  title?: string;
  description?: string;
};

export function ErrorState({
  title = "Something went wrong",
  description = "Please retry or contact support if the issue persists.",
}: ErrorStateProps) {
  return (
    <div
      className="flex min-h-72 flex-col items-center justify-center rounded-[28px] border border-red-200 bg-white/90 px-6 py-10 text-center shadow-sm dark:border-red-950 dark:bg-slate-900/80"
      role="alert"
    >
      <span className="flex h-14 w-14 items-center justify-center rounded-full bg-red-50 text-red-600 dark:bg-red-950/60 dark:text-red-300">
        <TriangleAlert className="h-6 w-6" aria-hidden="true" />
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
