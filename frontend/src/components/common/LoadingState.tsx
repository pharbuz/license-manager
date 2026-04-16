import { LoaderCircle, Sparkles } from "lucide-react";

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
      className="relative overflow-hidden rounded-[28px] border border-slate-200 bg-white/90 px-6 py-10 shadow-sm dark:border-slate-800 dark:bg-slate-900/80"
      role="status"
      aria-live="polite"
    >
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -left-8 top-0 h-32 w-32 rounded-full bg-blue-200/30 blur-3xl dark:bg-blue-500/10" />
        <div className="absolute bottom-0 right-0 h-36 w-36 rounded-full bg-cyan-200/30 blur-3xl dark:bg-cyan-500/10" />
      </div>

      <div className="relative flex min-h-72 flex-col items-center justify-center text-center">
        <span className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-50 to-cyan-100 text-blue-600 shadow-lg shadow-blue-500/10 dark:from-blue-950/80 dark:to-cyan-950/70 dark:text-blue-300">
          <div className="relative">
            <LoaderCircle className="h-7 w-7 animate-spin" aria-hidden="true" />
            <Sparkles className="absolute -right-3 -top-3 h-3.5 w-3.5 animate-pulse text-cyan-500 dark:text-cyan-300" />
          </div>
        </span>

        <h2 className="mt-5 text-lg font-semibold text-slate-950 dark:text-white">
          {title}
        </h2>
        <p className="mt-2 max-w-md text-sm text-slate-500 dark:text-slate-400">
          {description}
        </p>

        <div className="mt-8 w-full max-w-sm space-y-3" aria-hidden="true">
          <div className="h-3 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">
            <div className="h-full w-2/3 animate-loading-bar rounded-full bg-gradient-to-r from-blue-500 via-cyan-400 to-blue-500" />
          </div>
          <div className="grid gap-2">
            <div className="h-3 w-full animate-pulse rounded-full bg-slate-100 dark:bg-slate-800" />
            <div className="h-3 w-5/6 animate-pulse rounded-full bg-slate-100 dark:bg-slate-800" />
            <div className="h-3 w-2/3 animate-pulse rounded-full bg-slate-100 dark:bg-slate-800" />
          </div>
        </div>
      </div>
    </div>
  );
}
