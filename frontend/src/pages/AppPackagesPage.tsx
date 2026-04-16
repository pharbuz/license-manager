import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import type { ApiError } from "../api";
import { ConfirmDialog, FormModal, Modal } from "../components/modals";
import { ResourceListPage } from "../components/views/ResourceListPage";
import { downloadBlob } from "../utils/download";
import {
  createAppPackage,
  deleteAppPackage,
  downloadAppPackage,
  listAppPackages,
  notifyAppPackage,
  updateAppPackage,
} from "../services";
import type {
  AppPackage,
  AppPackageCreateInput,
  AppPackageUpdateInput,
  CollectionPage,
} from "../types";
import { buildCollectionPage } from "../utils/client-pagination";

type AppPackageFormValues = {
  versionNumber: string;
  binaryName: string;
  gemFuryUrl: string;
  binaryUrl: string;
};

type AppPackageDialogState =
  | { mode: "create" }
  | { mode: "edit"; appPackage: AppPackage }
  | null;

const defaultValues: AppPackageFormValues = {
  versionNumber: "",
  binaryName: "",
  gemFuryUrl: "",
  binaryUrl: "",
};

export function AppPackagesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [dialog, setDialog] = useState<AppPackageDialogState>(null);
  const [viewItem, setViewItem] = useState<AppPackage | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<AppPackage | null>(null);

  const query = useQuery<AppPackage[], ApiError>({
    queryKey: ["app-packages"],
    queryFn: () => listAppPackages(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: AppPackageCreateInput) => createAppPackage(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["app-packages"] });
      setDialog(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      appPackageId,
      payload,
    }: {
      appPackageId: string;
      payload: AppPackageUpdateInput;
    }) => updateAppPackage(appPackageId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["app-packages"] });
      setDialog(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (appPackageId: string) => deleteAppPackage(appPackageId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["app-packages"] });
      setDeleteTarget(null);
    },
  });

  const notifyMutation = useMutation({
    mutationFn: ({
      appPackageId,
      versionId,
    }: {
      appPackageId: string;
      versionId: string;
    }) => notifyAppPackage(appPackageId, versionId),
  });

  const dialogValues = useMemo(() => {
    if (dialog?.mode === "edit") {
      return {
        versionNumber: dialog.appPackage.versionNumber,
        binaryName: dialog.appPackage.binaryName,
        gemFuryUrl: dialog.appPackage.gemFuryUrl,
        binaryUrl: dialog.appPackage.binaryUrl,
      } satisfies AppPackageFormValues;
    }

    return defaultValues;
  }, [dialog]);

  const pagination: CollectionPage<AppPackage> | undefined = query.data
    ? buildCollectionPage({
        items: query.data,
        search,
        page,
        size: 10,
        searchValues: (appPackage) => [
          appPackage.versionNumber,
          appPackage.binaryName,
          appPackage.gemFuryUrl,
          appPackage.binaryUrl,
        ],
      })
    : undefined;

  const items = pagination?.items ?? [];
  const isEmpty = query.isSuccess && pagination?.total === 0;

  async function handleSubmit(values: AppPackageFormValues) {
    const payload = {
      versionNumber: values.versionNumber.trim(),
      binaryName: values.binaryName.trim(),
      gemFuryUrl: values.gemFuryUrl.trim(),
      binaryUrl: values.binaryUrl.trim(),
    } satisfies AppPackageCreateInput;

    if (dialog?.mode === "edit") {
      await updateMutation.mutateAsync({
        appPackageId: dialog.appPackage.id,
        payload,
      });
      return;
    }

    await createMutation.mutateAsync(payload);
  }

  async function handleDownload(appPackage: AppPackage) {
    const filePath = window.prompt(
      "Enter the file path to download",
      appPackage.binaryUrl,
    );
    if (!filePath) {
      return;
    }

    const blob = await downloadAppPackage(appPackage.id, filePath);
    downloadBlob(
      blob,
      appPackage.binaryName || `${appPackage.versionNumber}.bin`,
    );
  }

  return (
    <ResourceListPage<AppPackage>
      title="App Packages"
      description="Manage downloadable application packages and notification actions."
      search={search}
      onSearchChange={(value) => {
        setSearch(value);
        setPage(1);
      }}
      searchPlaceholder="Search app packages"
      createLabel="Add package"
      onCreate={() => setDialog({ mode: "create" })}
      columns={[
        { header: "Version", render: (item) => item.versionNumber },
        { header: "Binary", render: (item) => item.binaryName },
        { header: "GemFury URL", render: (item) => item.gemFuryUrl },
        { header: "Binary URL", render: (item) => item.binaryUrl },
      ]}
      items={items}
      rowLabel={(item) => item.id}
      rowActions={[
        { label: "View", onClick: (item) => setViewItem(item) },
        {
          label: "Edit",
          onClick: (item) => setDialog({ mode: "edit", appPackage: item }),
        },
        { label: "Download", onClick: (item) => void handleDownload(item) },
        {
          label: "Notify",
          onClick: (item) =>
            notifyMutation.mutate({
              appPackageId: item.id,
              versionId: item.id,
            }),
        },
        {
          label: "Delete",
          tone: "danger",
          onClick: (item) => setDeleteTarget(item),
        },
      ]}
      isLoading={query.isLoading}
      isError={query.isError}
      errorMessage={query.error?.message}
      isEmpty={isEmpty}
      emptyTitle="No app packages found"
      emptyDescription="Create a package to enable download and notify flows."
      page={pagination?.page}
      pages={pagination?.pages}
      total={pagination?.total}
      onPageChange={setPage}
      children={
        <>
          {dialog ? (
            <FormModal<AppPackageFormValues>
              key={`${dialog.mode}-${dialog.mode === "edit" ? dialog.appPackage.id : "new"}`}
              title={
                dialog.mode === "edit" ? "Edit app package" : "Add app package"
              }
              description="Capture the package binary and URLs."
              initialValues={dialogValues}
              fields={[
                {
                  name: "versionNumber",
                  label: "Version number",
                  required: true,
                },
                { name: "binaryName", label: "Binary name", required: true },
                { name: "gemFuryUrl", label: "GemFury URL", required: true },
                { name: "binaryUrl", label: "Binary URL", required: true },
              ]}
              submitLabel={
                dialog.mode === "edit" ? "Update package" : "Create package"
              }
              onSubmit={handleSubmit}
              onClose={() => setDialog(null)}
            />
          ) : null}

          {viewItem ? (
            <Modal
              title={viewItem.versionNumber}
              description={viewItem.binaryName}
              onClose={() => setViewItem(null)}
            >
              <dl className="lm-details">
                <div>
                  <dt>GemFury URL</dt>
                  <dd>{viewItem.gemFuryUrl}</dd>
                </div>
                <div>
                  <dt>Binary URL</dt>
                  <dd>{viewItem.binaryUrl}</dd>
                </div>
              </dl>
            </Modal>
          ) : null}

          {deleteTarget ? (
            <ConfirmDialog
              title="Delete app package"
              description={`Delete ${deleteTarget.versionNumber}? This action cannot be undone.`}
              confirmLabel={
                deleteMutation.isPending ? "Deleting..." : "Delete package"
              }
              danger
              onClose={() => setDeleteTarget(null)}
              onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
            />
          ) : null}
        </>
      }
    />
  );
}
