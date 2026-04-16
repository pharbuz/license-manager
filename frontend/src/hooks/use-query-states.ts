import type { CollectionPage } from "../types";

export type CollectionUiState = {
  isEmpty: boolean;
  hasItems: boolean;
};

export function getCollectionUiState<T>(
  data: CollectionPage<T> | undefined,
  isSuccess: boolean,
): CollectionUiState {
  const hasItems = (data?.items.length ?? 0) > 0;

  return {
    isEmpty: isSuccess && !hasItems,
    hasItems,
  };
}
