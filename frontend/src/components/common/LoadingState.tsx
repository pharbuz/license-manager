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
      className="lm-ui-state lm-ui-state--loading"
      role="status"
      aria-live="polite"
    >
      <span className="lm-ui-state__spinner" aria-hidden="true" />
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}
