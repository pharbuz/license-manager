import { LoaderCircle } from "lucide-react";

type LoadingStateProps = {
  title?: string;
  description?: string;
};

export function LoadingState({
  title = "Loading",
  description = "Please wait while data is being prepared.",
}: LoadingStateProps) {
  return (
    <div
      className="flex min-h-72 flex-col items-center justify-center rounded-[28px] border border-slate-200 bg-white/90 px-6 py-10 text-center shadow-sm dark:border-slate-800 dark:bg-slate-900/80"
      role="status"
      aria-live="polite"
    >
      <span className="flex h-14 w-14 items-center justify-center rounded-full bg-blue-50 text-blue-600 dark:bg-blue-950/60 dark:text-blue-300">
        <LoaderCircle className="h-6 w-6 animate-spin" aria-hidden="true" />
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
