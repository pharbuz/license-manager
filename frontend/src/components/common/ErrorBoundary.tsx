import { House, RefreshCw, TriangleAlert } from "lucide-react";
import {
  Component,
  type ErrorInfo,
  type PropsWithChildren,
  type ReactNode,
} from "react";
import { Link, useLocation } from "react-router-dom";

type ErrorBoundaryProps = PropsWithChildren<{
  title?: string;
  description?: string;
  homePath?: string;
  fullScreen?: boolean;
  resetKey?: string;
}>;

type ErrorBoundaryState = {
  error: Error | null;
};

const initialState: ErrorBoundaryState = {
  error: null,
};

function ErrorBoundaryFallback({
  description,
  error,
  fullScreen = true,
  homePath = "/",
  onRetry,
  title = "Unexpected application error",
}: Omit<ErrorBoundaryProps, "children" | "resetKey"> & {
  error: Error;
  onRetry: () => void;
}) {
  const content = (
    <div
      className="rounded-[28px] border border-red-200 bg-white/92 p-6 shadow-xl shadow-slate-950/10 backdrop-blur dark:border-red-950 dark:bg-slate-900/85"
      role="alert"
    >
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-red-50 text-red-600 dark:bg-red-950/60 dark:text-red-300">
        <TriangleAlert className="h-6 w-6" aria-hidden="true" />
      </div>

      <h1 className="mt-5 text-2xl font-bold tracking-tight text-slate-950 dark:text-white">
        {title}
      </h1>
      <p className="mt-3 max-w-2xl text-sm text-slate-500 dark:text-slate-400">
        {description ??
          "The current view crashed while rendering. You can retry the same screen or return to a safe route."}
      </p>

      <div className="mt-4 rounded-2xl border border-slate-200 bg-slate-50/80 p-4 dark:border-slate-800 dark:bg-slate-950/60">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400 dark:text-slate-500">
          Error details
        </p>
        <p className="mt-2 break-words text-sm font-medium text-slate-700 dark:text-slate-200">
          {error.message || "Unknown render error"}
        </p>
      </div>

      <div className="mt-6 flex flex-col gap-3 sm:flex-row">
        <button
          type="button"
          className="inline-flex items-center justify-center gap-2 rounded-2xl bg-blue-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-blue-500/20 transition hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-400/40"
          onClick={onRetry}
        >
          <RefreshCw className="h-4 w-4" />
          <span>Try again</span>
        </button>

        <Link
          className="inline-flex items-center justify-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 transition hover:border-blue-200 hover:text-slate-950 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200 dark:hover:border-slate-600 dark:hover:text-white"
          to={homePath}
        >
          <House className="h-4 w-4" />
          <span>Go to safe page</span>
        </Link>
      </div>
    </div>
  );

  if (fullScreen) {
    return (
      <section className="auth-screen">
        <div className="auth-screen__content auth-screen__content--wide">
          {content}
        </div>
      </section>
    );
  }

  return (
    <section className="mx-auto flex min-h-[calc(100vh-73px)] w-full max-w-[1600px] items-center px-4 py-6 sm:px-6 lg:px-8">
      <div className="w-full">{content}</div>
    </section>
  );
}

class ErrorBoundaryRoot extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  override state = initialState;

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error };
  }

  override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Unhandled frontend render error", error, errorInfo);
  }

  override componentDidUpdate(prevProps: ErrorBoundaryProps) {
    if (this.state.error && prevProps.resetKey !== this.props.resetKey) {
      this.setState(initialState);
    }
  }

  private handleRetry = () => {
    this.setState(initialState);
  };

  override render(): ReactNode {
    const { children, description, fullScreen, homePath, title } = this.props;

    if (this.state.error) {
      return (
        <ErrorBoundaryFallback
          description={description}
          error={this.state.error}
          fullScreen={fullScreen}
          homePath={homePath}
          onRetry={this.handleRetry}
          title={title}
        />
      );
    }

    return children;
  }
}

export function ErrorBoundary(props: Omit<ErrorBoundaryProps, "resetKey">) {
  const location = useLocation();

  return <ErrorBoundaryRoot {...props} resetKey={location.key} />;
}
