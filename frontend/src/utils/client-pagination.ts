import type { CollectionPage } from "../types";

type SearchableValue = string | number | boolean | null | undefined;

type BuildCollectionPageOptions<T> = {
  items: T[];
  page?: number;
  size?: number;
  search?: string | null;
  searchValues?: (item: T) => SearchableValue[];
  filter?: (item: T) => boolean;
};

const DEFAULT_PAGE_SIZE = 10;

export function buildCollectionPage<T>({
  items,
  page = 1,
  size = DEFAULT_PAGE_SIZE,
  search,
  searchValues,
  filter,
}: BuildCollectionPageOptions<T>): CollectionPage<T> {
  const normalizedSearch = normalizeSearchValue(search);

  const filteredItems = items.filter((item) => {
    if (filter && !filter(item)) {
      return false;
    }

    if (!normalizedSearch) {
      return true;
    }

    const values = searchValues?.(item) ?? [JSON.stringify(item)];

    return values.some((value) =>
      normalizeSearchValue(value).includes(normalizedSearch),
    );
  });

  const normalizedSize = size > 0 ? size : DEFAULT_PAGE_SIZE;
  const total = filteredItems.length;
  const pages = total === 0 ? 0 : Math.ceil(total / normalizedSize);
  const currentPage = pages === 0 ? 1 : Math.min(Math.max(page, 1), pages);
  const start = (currentPage - 1) * normalizedSize;

  return {
    items: filteredItems.slice(start, start + normalizedSize),
    total,
    page: currentPage,
    size: normalizedSize,
    pages,
  };
}

function normalizeSearchValue(value: SearchableValue): string {
  return String(value ?? "")
    .trim()
    .toLowerCase();
}
