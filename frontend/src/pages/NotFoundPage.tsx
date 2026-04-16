import { ErrorState, PageContainer } from "../components/common";

export function NotFoundPage() {
  return (
    <PageContainer
      title="Page not found"
      description="The requested location is not part of the current navigation map."
    >
      <ErrorState
        title="Route is unavailable"
        description="Use the sidebar navigation to move to a supported section."
      />
    </PageContainer>
  );
}
