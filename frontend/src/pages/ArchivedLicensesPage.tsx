import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import type { ApiError } from "../api";
import { ConfirmDialog, Modal } from "../components/modals";
import { ResourceListPage } from "../components/views/ResourceListPage";
import {
  deleteLicense,
  listArchivedLicenses,
  unarchiveLicense,
} from "../services";
import type { CollectionPage, License } from "../types";
import { buildCollectionPage } from "../utils/client-pagination";

export function ArchivedLicensesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewLicense, setViewLicense] = useState<License | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<License | null>(null);

  const query = useQuery<License[], ApiError>({
    queryKey: ["licenses", "archived"],
    queryFn: () => listArchivedLicenses(),
  });

  const unarchiveMutation = useMutation({
    mutationFn: (licenseId: string) => unarchiveLicense(licenseId),
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
        ],
      })
    : undefined;

  const items = pagination?.items ?? [];
  const isEmpty = query.isSuccess && pagination?.total === 0;

  return (
    <ResourceListPage<License>
      title="Archived Licenses"
      description="Restore or permanently delete archived licenses."
      search={search}
      onSearchChange={(value) => {
        setSearch(value);
        setPage(1);
      }}
      searchPlaceholder="Search archived licenses"
      columns={[
        { header: "Key", render: (item) => item.licenseKey },
        { header: "Email", render: (item) => item.licenseEmail },
        { header: "State", render: (item) => item.licenseState },
      ]}
      items={items}
      rowLabel={(item) => item.id}
      rowActions={[
        { label: "View", onClick: (item) => setViewLicense(item) },
        {
          label: "Unarchive",
          onClick: (item) => unarchiveMutation.mutate(item.id),
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
      emptyTitle="No archived licenses"
      emptyDescription="Archived licenses will appear here once lifecycle actions are used."
      page={pagination?.page}
      pages={pagination?.pages}
      total={pagination?.total}
      onPageChange={setPage}
      children={
        <>
          {viewLicense ? (
            <Modal
              title={viewLicense.licenseKey}
              description="Archived license details"
              onClose={() => setViewLicense(null)}
            >
              <dl className="lm-details">
                <div>
                  <dt>Email</dt>
                  <dd>{viewLicense.licenseEmail}</dd>
                </div>
                <div>
                  <dt>State</dt>
                  <dd>{viewLicense.licenseState}</dd>
                </div>
                <div>
                  <dt>Count</dt>
                  <dd>{viewLicense.licenseCount}</dd>
                </div>
              </dl>
            </Modal>
          ) : null}

          {deleteTarget ? (
            <ConfirmDialog
              title="Delete archived license"
              description={`Delete ${deleteTarget.licenseKey} permanently?`}
              confirmLabel={
                deleteMutation.isPending ? "Deleting..." : "Delete license"
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
