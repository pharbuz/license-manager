type EmptyStateProps = {
  title?: string;
  description?: string;
};

export function EmptyState({
  title = "No data yet",
  description = "Create your first record to populate this view.",
}: EmptyStateProps) {
  return (
    <div className="lm-ui-state" role="status" aria-live="polite">
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  );
}
