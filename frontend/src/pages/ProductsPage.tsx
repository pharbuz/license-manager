import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import type { ApiError } from "../api";
import { ConfirmDialog, FormModal, Modal } from "../components/modals";
import { ResourceListPage } from "../components/views/ResourceListPage";
import {
  createProduct,
  deleteProduct,
  listProducts,
  updateProduct,
} from "../services";
import type {
  CollectionPage,
  Product,
  ProductCreateInput,
  ProductUpdateInput,
} from "../types";
import { buildCollectionPage } from "../utils/client-pagination";

type ProductFormValues = {
  name: string;
  kind: string;
};

const defaultProductValues: ProductFormValues = { name: "", kind: "" };

type ProductDialogState =
  | { mode: "create" }
  | { mode: "edit"; product: Product }
  | null;

export function ProductsPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [dialog, setDialog] = useState<ProductDialogState>(null);
  const [viewProduct, setViewProduct] = useState<Product | null>(null);
  const [deleteProductTarget, setDeleteProductTarget] =
    useState<Product | null>(null);

  const query = useQuery<Product[], ApiError>({
    queryKey: ["products"],
    queryFn: () => listProducts(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: ProductCreateInput) => createProduct(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["products"] });
      setDialog(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      productId,
      payload,
    }: {
      productId: string;
      payload: ProductUpdateInput;
    }) => updateProduct(productId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["products"] });
      setDialog(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (productId: string) => deleteProduct(productId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["products"] });
      setDeleteProductTarget(null);
    },
  });

  const dialogValues = useMemo(() => {
    if (dialog?.mode === "edit") {
      return {
        name: dialog.product.name,
        kind: dialog.product.kind,
      } satisfies ProductFormValues;
    }

    return defaultProductValues;
  }, [dialog]);

  const pagination: CollectionPage<Product> | undefined = query.data
    ? buildCollectionPage({
        items: query.data,
        search,
        page,
        size: 10,
        searchValues: (product) => [product.name, product.kind],
      })
    : undefined;

  const items = pagination?.items ?? [];
  const isEmpty = query.isSuccess && pagination?.total === 0;

  async function handleSubmit(values: ProductFormValues) {
    const payload = {
      name: values.name.trim(),
      kind: values.kind.trim(),
    } satisfies ProductCreateInput;

    if (dialog?.mode === "edit") {
      await updateMutation.mutateAsync({
        productId: dialog.product.id,
        payload,
      });
      return;
    }

    await createMutation.mutateAsync(payload);
  }

  return (
    <ResourceListPage<Product>
      title="Products"
      description="Manage products and their associated kind values."
      search={search}
      onSearchChange={(value) => {
        setSearch(value);
        setPage(1);
      }}
      searchPlaceholder="Search products"
      createLabel="Add product"
      onCreate={() => setDialog({ mode: "create" })}
      columns={[
        { header: "Name", render: (item) => item.name },
        { header: "Kind", render: (item) => item.kind },
      ]}
      items={items}
      rowLabel={(item) => item.id}
      rowActions={[
        { label: "View", onClick: (item) => setViewProduct(item) },
        {
          label: "Edit",
          onClick: (item) => setDialog({ mode: "edit", product: item }),
        },
        {
          label: "Delete",
          tone: "danger",
          onClick: (item) => setDeleteProductTarget(item),
        },
      ]}
      isLoading={query.isLoading}
      isError={query.isError}
      errorMessage={query.error?.message}
      isEmpty={isEmpty}
      emptyTitle="No products found"
      emptyDescription="Create a product to link it with licenses and customers."
      page={pagination?.page}
      pages={pagination?.pages}
      total={pagination?.total}
      onPageChange={setPage}
      children={
        <>
          {dialog ? (
            <FormModal<ProductFormValues>
              key={`${dialog.mode}-${dialog.mode === "edit" ? dialog.product.id : "new"}`}
              title={dialog.mode === "edit" ? "Edit product" : "Add product"}
              description="Capture the product name and kind label."
              initialValues={dialogValues}
              fields={[
                { name: "name", label: "Name", required: true },
                { name: "kind", label: "Kind", required: true },
              ]}
              submitLabel={
                dialog.mode === "edit" ? "Update product" : "Create product"
              }
              onSubmit={handleSubmit}
              onClose={() => setDialog(null)}
            />
          ) : null}

          {viewProduct ? (
            <Modal
              title={viewProduct.name}
              description={viewProduct.kind}
              onClose={() => setViewProduct(null)}
            >
              <dl className="lm-details">
                <div>
                  <dt>Name</dt>
                  <dd>{viewProduct.name}</dd>
                </div>
                <div>
                  <dt>Kind</dt>
                  <dd>{viewProduct.kind}</dd>
                </div>
              </dl>
            </Modal>
          ) : null}

          {deleteProductTarget ? (
            <ConfirmDialog
              title="Delete product"
              description={`Delete ${deleteProductTarget.name}? This action cannot be undone.`}
              confirmLabel={
                deleteMutation.isPending ? "Deleting..." : "Delete product"
              }
              danger
              onClose={() => setDeleteProductTarget(null)}
              onConfirm={() => deleteMutation.mutate(deleteProductTarget.id)}
            />
          ) : null}
        </>
      }
    />
  );
}
