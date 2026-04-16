import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import type { ApiError } from "../api";
import { ConfirmDialog, FormModal, Modal } from "../components/modals";
import { ResourceListPage } from "../components/views/ResourceListPage";
import { toDateTimeLocalValue, toIsoDateTimeValue } from "../utils/dates";
import {
  archiveLicense,
  createLicense,
  deleteLicense,
  generateLicense,
  listLicenses,
  updateLicense,
} from "../services";
import type {
  CollectionPage,
  License,
  LicenseCreateInput,
  LicenseGenerateInput,
  LicenseGeneratedKey,
  LicenseUpdateInput,
} from "../types";
import { buildCollectionPage } from "../utils/client-pagination";

type LicenseFormValues = {
  customerId: string;
  productId: string;
  kindId: string;
  licenseCount: number;
  licenseState: string;
  licenseKey: string;
  licenseEmail: string;
  doubleSend: boolean;
  beginDate: string;
  endDate: string;
  notificationDate: string;
};

type LicenseGenerateFormValues = {
  customerSymbol: string;
  endDate: string;
  licenseCount: number;
};

type LicenseDialogState =
  | { mode: "create" }
  | { mode: "edit"; license: License }
  | null;

const defaultLicenseValues: LicenseFormValues = {
  customerId: "",
  productId: "",
  kindId: "",
  licenseCount: 1,
  licenseState: "active",
  licenseKey: "",
  licenseEmail: "",
  doubleSend: false,
  beginDate: "",
  endDate: "",
  notificationDate: "",
};

const defaultGenerateValues: LicenseGenerateFormValues = {
  customerSymbol: "",
  endDate: "",
  licenseCount: 1,
};

function nullableUuid(value: string) {
  return value.trim() || null;
}

export function LicensesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [dialog, setDialog] = useState<LicenseDialogState>(null);
  const [viewLicense, setViewLicense] = useState<License | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<License | null>(null);
  const [generateKeyResult, setGenerateKeyResult] =
    useState<LicenseGeneratedKey | null>(null);
  const [generateFormOpen, setGenerateFormOpen] = useState(false);

  const query = useQuery<License[], ApiError>({
    queryKey: ["licenses"],
    queryFn: () => listLicenses(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: LicenseCreateInput) => createLicense(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["licenses"] });
      setDialog(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      licenseId,
      payload,
    }: {
      licenseId: string;
      payload: LicenseUpdateInput;
    }) => updateLicense(licenseId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["licenses"] });
      setDialog(null);
    },
  });

  const archiveMutation = useMutation({
    mutationFn: (licenseId: string) => archiveLicense(licenseId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["licenses"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (licenseId: string) => deleteLicense(licenseId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["licenses"] });
      setDeleteTarget(null);
    },
  });

  const generateMutation = useMutation({
    mutationFn: (payload: LicenseGenerateInput) => generateLicense(payload),
    onSuccess: (data) => {
      setGenerateKeyResult(data);
      setGenerateFormOpen(false);
    },
  });

  const [generateValues] = useState(defaultGenerateValues);

  const dialogValues = useMemo(() => {
    if (dialog?.mode === "edit") {
      return {
        customerId: dialog.license.customerId ?? "",
        productId: dialog.license.productId ?? "",
        kindId: dialog.license.kindId ?? "",
        licenseCount: dialog.license.licenseCount,
        licenseState: dialog.license.licenseState,
        licenseKey: dialog.license.licenseKey,
        licenseEmail: dialog.license.licenseEmail,
        doubleSend: dialog.license.doubleSend,
        beginDate: toDateTimeLocalValue(dialog.license.beginDate),
        endDate: toDateTimeLocalValue(dialog.license.endDate),
        notificationDate: toDateTimeLocalValue(dialog.license.notificationDate),
      } satisfies LicenseFormValues;
    }

    return defaultLicenseValues;
  }, [dialog]);

  const pagination: CollectionPage<License> | undefined = query.data
    ? buildCollectionPage({
        items: query.data,
        search,
        page,
        size: 10,
        searchValues: (license) => [
          license.licenseKey,
          license.licenseEmail,
          license.licenseState,
          license.customerId,
          license.productId,
          license.kindId,
        ],
      })
    : undefined;

  const items = pagination?.items ?? [];
  const isEmpty = query.isSuccess && pagination?.total === 0;

  async function handleSubmit(values: LicenseFormValues) {
    const payload = {
      customerId: nullableUuid(values.customerId),
      productId: nullableUuid(values.productId),
      kindId: nullableUuid(values.kindId),
      licenseCount: Number(values.licenseCount),
      licenseState: values.licenseState.trim(),
      licenseKey: values.licenseKey.trim(),
      licenseEmail: values.licenseEmail.trim(),
      doubleSend: values.doubleSend,
      beginDate: toIsoDateTimeValue(values.beginDate),
      endDate: toIsoDateTimeValue(values.endDate),
      notificationDate: toIsoDateTimeValue(values.notificationDate),
    } satisfies LicenseCreateInput;

    if (dialog?.mode === "edit") {
      await updateMutation.mutateAsync({
        licenseId: dialog.license.id,
        payload,
      });
      return;
    }

    await createMutation.mutateAsync(payload);
  }

  return (
    <ResourceListPage<License>
      title="Licenses"
      description="Manage active licenses, archive them, and generate new keys."
      search={search}
      onSearchChange={(value) => {
        setSearch(value);
        setPage(1);
      }}
      searchPlaceholder="Search licenses"
      createLabel="Add license"
      onCreate={() => setDialog({ mode: "create" })}
      headerActions={
        <button
          type="button"
          className="lm-button"
          onClick={() => setGenerateFormOpen(true)}
        >
          Generate key
        </button>
      }
      columns={[
        { header: "Key", render: (item) => item.licenseKey },
        { header: "Email", render: (item) => item.licenseEmail },
        { header: "State", render: (item) => item.licenseState },
        { header: "Count", render: (item) => item.licenseCount },
        {
          header: "Ends",
          render: (item) => new Date(item.endDate).toLocaleDateString(),
        },
      ]}
      items={items}
      rowLabel={(item) => item.id}
      rowActions={[
        { label: "View", onClick: (item) => setViewLicense(item) },
        {
          label: "Edit",
          onClick: (item) => setDialog({ mode: "edit", license: item }),
        },
        {
          label: "Archive",
          onClick: (item) => archiveMutation.mutate(item.id),
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
      emptyTitle="No licenses found"
      emptyDescription="Create a license or generate a key to begin."
      page={pagination?.page}
      pages={pagination?.pages}
      total={pagination?.total}
      onPageChange={setPage}
      children={
        <>
          {dialog ? (
            <FormModal<LicenseFormValues>
              key={`${dialog.mode}-${dialog.mode === "edit" ? dialog.license.id : "new"}`}
              title={dialog.mode === "edit" ? "Edit license" : "Add license"}
              description="Capture the license record and lifecycle dates."
              initialValues={dialogValues}
              fields={[
                { name: "customerId", label: "Customer ID" },
                { name: "productId", label: "Product ID" },
                { name: "kindId", label: "Kind ID" },
                {
                  name: "licenseCount",
                  label: "License count",
                  type: "number",
                  required: true,
                },
                {
                  name: "licenseState",
                  label: "License state",
                  required: true,
                },
                { name: "licenseKey", label: "License key", required: true },
                {
                  name: "licenseEmail",
                  label: "License email",
                  type: "email",
                  required: true,
                },
                { name: "doubleSend", label: "Double send", type: "checkbox" },
                {
                  name: "beginDate",
                  label: "Begin date",
                  type: "datetime-local",
                  required: true,
                },
                {
                  name: "endDate",
                  label: "End date",
                  type: "datetime-local",
                  required: true,
                },
                {
                  name: "notificationDate",
                  label: "Notification date",
                  type: "datetime-local",
                  required: true,
                },
              ]}
              submitLabel={
                dialog.mode === "edit" ? "Update license" : "Create license"
              }
              onSubmit={handleSubmit}
              onClose={() => setDialog(null)}
            />
          ) : null}

          {viewLicense ? (
            <Modal
              title={viewLicense.licenseKey}
              description={viewLicense.licenseEmail}
              onClose={() => setViewLicense(null)}
            >
              <dl className="lm-details">
                <div>
                  <dt>State</dt>
                  <dd>{viewLicense.licenseState}</dd>
                </div>
                <div>
                  <dt>Count</dt>
                  <dd>{viewLicense.licenseCount}</dd>
                </div>
                <div>
                  <dt>Double send</dt>
                  <dd>{viewLicense.doubleSend ? "Yes" : "No"}</dd>
                </div>
                <div>
                  <dt>Customer</dt>
                  <dd>{viewLicense.customerId ?? "-"}</dd>
                </div>
                <div>
                  <dt>Product</dt>
                  <dd>{viewLicense.productId ?? "-"}</dd>
                </div>
                <div>
                  <dt>Kind</dt>
                  <dd>{viewLicense.kindId ?? "-"}</dd>
                </div>
              </dl>
            </Modal>
          ) : null}

          {deleteTarget ? (
            <ConfirmDialog
              title="Delete license"
              description={`Delete ${deleteTarget.licenseKey}? This action cannot be undone.`}
              confirmLabel={
                deleteMutation.isPending ? "Deleting..." : "Delete license"
              }
              danger
              onClose={() => setDeleteTarget(null)}
              onConfirm={() => deleteMutation.mutate(deleteTarget.id)}
            />
          ) : null}

          {generateKeyResult ? (
            <Modal
              title="Generated license key"
              description="Copy the generated key."
              onClose={() => setGenerateKeyResult(null)}
            >
              <p>{generateKeyResult.licenseKey}</p>
            </Modal>
          ) : null}

          {generateFormOpen ? (
            <FormModal<LicenseGenerateFormValues>
              key="generate-license"
              title="Generate license key"
              description="Create a key from the current customer and expiry inputs."
              initialValues={generateValues}
              fields={[
                { name: "customerSymbol", label: "Customer symbol" },
                {
                  name: "endDate",
                  label: "End date",
                  type: "datetime-local",
                  required: true,
                },
                {
                  name: "licenseCount",
                  label: "License count",
                  type: "number",
                  required: true,
                },
              ]}
              submitLabel={
                generateMutation.isPending ? "Generating..." : "Generate key"
              }
              onSubmit={async (values) => {
                await generateMutation.mutateAsync({
                  customerSymbol: values.customerSymbol.trim(),
                  endDate: toIsoDateTimeValue(values.endDate),
                  licenseCount: Number(values.licenseCount),
                });
              }}
              onClose={() => setGenerateFormOpen(false)}
            />
          ) : null}
        </>
      }
    />
  );
}
