type ErrorStateProps = {
  title?: string;
  description?: string;
};

export function ErrorState({
  title = "Something went wrong",
  description = "Please retry or contact support if the issue persists.",
}: ErrorStateProps) {
  return (
    <div className="lm-ui-state lm-ui-state--error" role="alert">
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}
