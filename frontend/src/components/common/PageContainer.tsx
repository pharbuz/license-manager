import type { ReactNode } from "react";

type PageContainerProps = {
  title: string;
  description?: string;
  actions?: ReactNode;
  children: ReactNode;
};

export function PageContainer({
  title,
  description,
  actions,
  children,
}: PageContainerProps) {
  return (
    <section
      className="mx-auto w-full max-w-[1600px] px-4 py-6 sm:px-6 lg:px-8"
      aria-labelledby="lm-page-title"
    >
      <header className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div className="min-w-0">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">
            Workspace
          </p>
          <h1
            id="lm-page-title"
            className="mt-2 text-3xl font-bold tracking-tight text-slate-950 dark:text-white"
          >
            {title}
          </h1>
          {description ? (
            <p className="mt-2 max-w-3xl text-sm text-slate-500 dark:text-slate-400">
              {description}
            </p>
          ) : null}
        </div>

        {actions ? <div className="shrink-0">{actions}</div> : null}
      </header>

      <div className="space-y-6">{children}</div>
    </section>
  );
}
