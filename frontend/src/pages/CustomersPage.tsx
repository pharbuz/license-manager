import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import type { ApiError } from "../api";
import { ConfirmDialog, FormModal, Modal } from "../components/modals";
import { ResourceListPage } from "../components/views/ResourceListPage";
import {
  createCustomer,
  deleteCustomer,
  listCustomers,
  updateCustomer,
} from "../services";
import type {
  CollectionPage,
  Customer,
  CustomerCreateInput,
  CustomerUpdateInput,
} from "../types";
import { buildCollectionPage } from "../utils/client-pagination";

type CustomerFormValues = {
  name: string;
  email: string;
  customerSymbol: string;
  notificationsEnabled: boolean;
  gemFuryUsed: boolean;
  contactPersonName: string;
  contactPersonPhone: string;
};

const defaultCustomerValues: CustomerFormValues = {
  name: "",
  email: "",
  customerSymbol: "",
  notificationsEnabled: true,
  gemFuryUsed: true,
  contactPersonName: "",
  contactPersonPhone: "",
};

type CustomerDialogState =
  | { mode: "create" }
  | { mode: "edit"; customer: Customer }
  | null;

export function CustomersPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [dialog, setDialog] = useState<CustomerDialogState>(null);
  const [viewCustomer, setViewCustomer] = useState<Customer | null>(null);
  const [deleteCustomerTarget, setDeleteCustomerTarget] =
    useState<Customer | null>(null);

  const query = useQuery<Customer[], ApiError>({
    queryKey: ["customers"],
    queryFn: () => listCustomers(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: CustomerCreateInput) => createCustomer(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["customers"] });
      setDialog(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({
      customerId,
      payload,
    }: {
      customerId: string;
      payload: CustomerUpdateInput;
    }) => updateCustomer(customerId, payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["customers"] });
      setDialog(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (customerId: string) => deleteCustomer(customerId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["customers"] });
      setDeleteCustomerTarget(null);
    },
  });

  const pagination: CollectionPage<Customer> | undefined = query.data
    ? buildCollectionPage({
        items: query.data,
        search,
        page,
        size: 10,
        searchValues: (customer) => [
          customer.customerSymbol,
          customer.name,
          customer.email,
          customer.contactPersonName,
          customer.contactPersonPhone,
        ],
      })
    : undefined;

  const items = pagination?.items ?? [];
  const isEmpty = query.isSuccess && pagination?.total === 0;

  const dialogValues = useMemo(() => {
    if (dialog?.mode === "edit") {
      const customer = dialog.customer;
      return {
        name: customer.name,
        email: customer.email,
        customerSymbol: customer.customerSymbol,
        notificationsEnabled: customer.notificationsEnabled,
        gemFuryUsed: customer.gemFuryUsed,
        contactPersonName: customer.contactPersonName ?? "",
        contactPersonPhone: customer.contactPersonPhone ?? "",
      } satisfies CustomerFormValues;
    }

    return defaultCustomerValues;
  }, [dialog]);

  async function handleSubmit(values: CustomerFormValues) {
    const payload = {
      name: values.name.trim(),
      email: values.email.trim(),
      customerSymbol: values.customerSymbol.trim(),
      notificationsEnabled: values.notificationsEnabled,
      gemFuryUsed: values.gemFuryUsed,
      contactPersonName: values.contactPersonName.trim() || null,
      contactPersonPhone: values.contactPersonPhone.trim() || null,
    } satisfies CustomerCreateInput;

    if (dialog?.mode === "edit") {
      await updateMutation.mutateAsync({
        customerId: dialog.customer.id,
        payload,
      });
      return;
    }

    await createMutation.mutateAsync(payload);
  }

  return (
    <ResourceListPage<Customer>
      title="Customers"
      description="Manage customer accounts, contacts, and notification preferences."
      search={search}
      onSearchChange={(value) => {
        setSearch(value);
        setPage(1);
      }}
      searchPlaceholder="Search customers"
      createLabel="Add customer"
      onCreate={() => setDialog({ mode: "create" })}
      columns={[
        { header: "Symbol", render: (item) => item.customerSymbol },
        { header: "Name", render: (item) => item.name },
        { header: "Email", render: (item) => item.email },
        {
          header: "Notifications",
          render: (item) =>
            item.notificationsEnabled ? "Enabled" : "Disabled",
        },
        {
          header: "GemFury",
          render: (item) => (item.gemFuryUsed ? "Used" : "Not used"),
        },
      ]}
      items={items}
      rowLabel={(item) => item.id}
      rowActions={[
        { label: "View", onClick: (item) => setViewCustomer(item) },
        {
          label: "Edit",
          onClick: (item) => setDialog({ mode: "edit", customer: item }),
        },
        {
          label: "Delete",
          tone: "danger",
          onClick: (item) => setDeleteCustomerTarget(item),
        },
      ]}
      isLoading={query.isLoading}
      isError={query.isError}
      errorMessage={query.error?.message}
      isEmpty={isEmpty}
      emptyTitle="No customers found"
      emptyDescription="Create a customer to start managing licenses and contacts."
      page={pagination?.page}
      pages={pagination?.pages}
      total={pagination?.total}
      onPageChange={setPage}
      children={
        <>
          {dialog ? (
            <FormModal<CustomerFormValues>
              key={`${dialog.mode}-${dialog.mode === "edit" ? dialog.customer.id : "new"}`}
              title={dialog.mode === "edit" ? "Edit customer" : "Add customer"}
              description="Capture the customer identity and notification settings."
              initialValues={dialogValues}
              fields={[
                { name: "name", label: "Name", required: true },
                {
                  name: "email",
                  label: "Email",
                  type: "email",
                  required: true,
                },
                {
                  name: "customerSymbol",
                  label: "Customer symbol",
                  required: true,
                },
                {
                  name: "notificationsEnabled",
                  label: "Notifications enabled",
                  type: "checkbox",
                },
                {
                  name: "gemFuryUsed",
                  label: "GemFury used",
                  type: "checkbox",
                },
                { name: "contactPersonName", label: "Contact person name" },
                { name: "contactPersonPhone", label: "Contact person phone" },
              ]}
              submitLabel={
                dialog.mode === "edit" ? "Update customer" : "Create customer"
              }
              onSubmit={handleSubmit}
              onClose={() => setDialog(null)}
            />
          ) : null}

          {viewCustomer ? (
            <Modal
              title={viewCustomer.name}
              description={viewCustomer.customerSymbol}
              onClose={() => setViewCustomer(null)}
            >
              <dl className="lm-details">
                <div>
                  <dt>Email</dt>
                  <dd>{viewCustomer.email}</dd>
                </div>
                <div>
                  <dt>Notifications</dt>
                  <dd>
                    {viewCustomer.notificationsEnabled ? "Enabled" : "Disabled"}
                  </dd>
                </div>
                <div>
                  <dt>GemFury</dt>
                  <dd>{viewCustomer.gemFuryUsed ? "Used" : "Not used"}</dd>
                </div>
                <div>
                  <dt>Contact name</dt>
                  <dd>{viewCustomer.contactPersonName ?? "-"}</dd>
                </div>
                <div>
                  <dt>Contact phone</dt>
                  <dd>{viewCustomer.contactPersonPhone ?? "-"}</dd>
                </div>
              </dl>
            </Modal>
          ) : null}

          {deleteCustomerTarget ? (
            <ConfirmDialog
              title="Delete customer"
              description={`Delete ${deleteCustomerTarget.name}? This action cannot be undone.`}
              confirmLabel={
                deleteMutation.isPending ? "Deleting..." : "Delete customer"
              }
              danger
              onClose={() => setDeleteCustomerTarget(null)}
              onConfirm={() => deleteMutation.mutate(deleteCustomerTarget.id)}
            />
          ) : null}
        </>
      }
    />
  );
}
