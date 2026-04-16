import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import type { ApiError } from "../api";
import { ConfirmDialog, FormModal, Modal } from "../components/modals";
import { ResourceListPage } from "../components/views/ResourceListPage";
import { createKind, deleteKind, listKinds, updateKind } from "../services";
import type {
  CollectionPage,
  Kind,
  KindCreateInput,
  KindUpdateInput,
} from "../types";
import { buildCollectionPage } from "../utils/client-pagination";

type KindFormValues = { name: string };

const defaultKindValues: KindFormValues = { name: "" };

type KindDialogState = { mode: "create" } | { mode: "edit"; kind: Kind } | null;

export function LicenseKindsPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [dialog, setDialog] = useState<KindDialogState>(null);
  const [viewKind, setViewKind] = useState<Kind | null>(null);
  const [deleteKindTarget, setDeleteKindTarget] = useState<Kind | null>(null);

  const query = useQuery<Kind[], ApiError>({
    queryKey: ["kinds"],
    queryFn: () => listKinds(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: KindCreateInput) => createKind(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["kinds"] });
      setDialog(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      kindId,
      payload,
    }: {
      kindId: string;
      payload: KindUpdateInput;
    }) => updateKind(kindId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["kinds"] });
      setDialog(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (kindId: string) => deleteKind(kindId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["kinds"] });
      setDeleteKindTarget(null);
    },
  });

  const dialogValues = useMemo(() => {
    if (dialog?.mode === "edit") {
      return { name: dialog.kind.name } satisfies KindFormValues;
    }

    return defaultKindValues;
  }, [dialog]);

  const pagination: CollectionPage<Kind> | undefined = query.data
    ? buildCollectionPage({
        items: query.data,
        search,
        page,
        size: 10,
        searchValues: (kind) => [kind.name],
      })
    : undefined;

  const items = pagination?.items ?? [];
  const isEmpty = query.isSuccess && pagination?.total === 0;

  async function handleSubmit(values: KindFormValues) {
    const payload = { name: values.name.trim() } satisfies KindCreateInput;

    if (dialog?.mode === "edit") {
      await updateMutation.mutateAsync({ kindId: dialog.kind.id, payload });
      return;
    }

    await createMutation.mutateAsync(payload);
  }

  return (
    <ResourceListPage<Kind>
      title="License Kinds"
      description="Manage licensing categories and their labels."
      search={search}
      onSearchChange={(value) => {
        setSearch(value);
        setPage(1);
      }}
      searchPlaceholder="Search kinds"
      createLabel="Add kind"
      onCreate={() => setDialog({ mode: "create" })}
      columns={[
        { header: "Name", render: (item) => item.name },
        {
          header: "Modified",
          render: (item) => new Date(item.modifiedAt).toLocaleString(),
        },
      ]}
      items={items}
      rowLabel={(item) => item.id}
      rowActions={[
        { label: "View", onClick: (item) => setViewKind(item) },
        {
          label: "Edit",
          onClick: (item) => setDialog({ mode: "edit", kind: item }),
        },
        {
          label: "Delete",
          tone: "danger",
          onClick: (item) => setDeleteKindTarget(item),
        },
      ]}
      isLoading={query.isLoading}
      isError={query.isError}
      errorMessage={query.error?.message}
      isEmpty={isEmpty}
      emptyTitle="No kinds found"
      emptyDescription="Create a kind to organize product and license types."
      page={pagination?.page}
      pages={pagination?.pages}
      total={pagination?.total}
      onPageChange={setPage}
      children={
        <>
          {dialog ? (
            <FormModal<KindFormValues>
              key={`${dialog.mode}-${dialog.mode === "edit" ? dialog.kind.id : "new"}`}
              title={dialog.mode === "edit" ? "Edit kind" : "Add kind"}
              description="Capture the kind name."
              initialValues={dialogValues}
              fields={[{ name: "name", label: "Name", required: true }]}
              submitLabel={
                dialog.mode === "edit" ? "Update kind" : "Create kind"
              }
              onSubmit={handleSubmit}
              onClose={() => setDialog(null)}
            />
          ) : null}

          {viewKind ? (
            <Modal
              title={viewKind.name}
              description="Kind details"
              onClose={() => setViewKind(null)}
            >
              <dl className="lm-details">
                <div>
                  <dt>Name</dt>
                  <dd>{viewKind.name}</dd>
                </div>
              </dl>
            </Modal>
          ) : null}

          {deleteKindTarget ? (
            <ConfirmDialog
              title="Delete kind"
              description={`Delete ${deleteKindTarget.name}? This action cannot be undone.`}
              confirmLabel={
                deleteMutation.isPending ? "Deleting..." : "Delete kind"
              }
              danger
              onClose={() => setDeleteKindTarget(null)}
              onConfirm={() => deleteMutation.mutate(deleteKindTarget.id)}
            />
          ) : null}
        </>
      }
    />
  );
}
