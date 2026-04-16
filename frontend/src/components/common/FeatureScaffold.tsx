import type { ReactNode } from "react";
import { EmptyState } from "./EmptyState";
import { PageContainer } from "./PageContainer";

type FeatureScaffoldProps = {
  title: string;
  description: string;
  endpoint: string;
  actions?: ReactNode;
};

export function FeatureScaffold({
  title,
  description,
  endpoint,
  actions,
}: FeatureScaffoldProps) {
  return (
    <PageContainer title={title} description={description} actions={actions}>
      <div className="feature-scaffold__card" role="note">
        <strong>Endpoint:</strong> {endpoint}
      </div>

      <EmptyState
        title="View is ready for data"
        description="This route is wired and waiting for list/detail hooks to provide records."
      />
    </PageContainer>
  );
}
