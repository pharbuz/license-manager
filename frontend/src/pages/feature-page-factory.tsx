import { FeatureScaffold } from "../components/common/FeatureScaffold";

type FeaturePageProps = {
  title: string;
  description: string;
  endpoint: string;
};

export function FeaturePageFactory({
  title,
  description,
  endpoint,
}: FeaturePageProps) {
  return (
    <FeatureScaffold
      title={title}
      description={description}
      endpoint={endpoint}
    />
  );
}
