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
    <section className="lm-page-container" aria-labelledby="lm-page-title">
      <header className="lm-page-container__header">
        <div>
          <h1 id="lm-page-title">{title}</h1>
          {description ? <p>{description}</p> : null}
        </div>
        {actions ? <div>{actions}</div> : null}
      </header>

      <div className="lm-page-container__body">{children}</div>
    </section>
  );
}
