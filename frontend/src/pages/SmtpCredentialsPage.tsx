import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import type { ApiError } from "../api";
import { ConfirmDialog, FormModal, Modal } from "../components/modals";
import { PageContainer } from "../components/common";
import {
  createSmtpCredentials,
  deleteSmtpCredentials,
  getSmtpCredentials,
  updateSmtpCredentials,
} from "../services";
import type {
  SmtpCredential,
  SmtpCredentialCreateInput,
  SmtpCredentialUpdateInput,
} from "../types";

type SmtpFormValues = {
  host: string;
  port: number;
  username: string;
  password: string;
  senderEmail: string;
  useTls: boolean;
  useSsl: boolean;
};

const defaultValues: SmtpFormValues = {
  host: "",
  port: 587,
  username: "",
  password: "",
  senderEmail: "",
  useTls: true,
  useSsl: false,
};

export function SmtpCredentialsPage() {
  const queryClient = useQueryClient();
  const [editing, setEditing] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [viewOpen, setViewOpen] = useState(false);

  const query = useQuery<SmtpCredential, ApiError>({
    queryKey: ["smtp-credentials"],
    queryFn: () => getSmtpCredentials(),
  });

  const createMutation = useMutation({
    mutationFn: (payload: SmtpCredentialCreateInput) =>
      createSmtpCredentials(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["smtp-credentials"] });
      setEditing(false);
    },
  });

  const updateMutation = useMutation({
    mutationFn: (payload: SmtpCredentialUpdateInput) =>
      updateSmtpCredentials(payload),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["smtp-credentials"] });
      setEditing(false);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteSmtpCredentials(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["smtp-credentials"] });
      setDeleteOpen(false);
    },
  });

  const item = query.data ?? null;

  return (
    <PageContainer
      title="SMTP Credentials"
      description="Create and maintain the outgoing mail credentials used by notification flows."
      actions={
        <div className="lm-row-actions">
          <button
            className="lm-button"
            type="button"
            onClick={() => setViewOpen(true)}
            disabled={!item}
          >
            View
          </button>
          <button
            className="lm-button lm-button--primary"
            type="button"
            onClick={() => setEditing(true)}
          >
            {item ? "Edit credentials" : "Create credentials"}
          </button>
          <button
            className="lm-button lm-button--danger"
            type="button"
            onClick={() => setDeleteOpen(true)}
            disabled={!item}
          >
            Delete
          </button>
        </div>
      }
    >
      <section className="feature-scaffold__card">
        {query.isLoading ? (
          <p>Loading SMTP credentials...</p>
        ) : query.isError ? (
          <p>{query.error?.message}</p>
        ) : item ? (
          <dl className="lm-details">
            <div>
              <dt>Secret name</dt>
              <dd>{item.secretName}</dd>
            </div>
            <div>
              <dt>Host</dt>
              <dd>{item.host}</dd>
            </div>
            <div>
              <dt>Port</dt>
              <dd>{item.port}</dd>
            </div>
            <div>
              <dt>Username</dt>
              <dd>{item.username}</dd>
            </div>
            <div>
              <dt>Sender email</dt>
              <dd>{item.senderEmail ?? "-"}</dd>
            </div>
            <div>
              <dt>TLS</dt>
              <dd>{item.useTls ? "Enabled" : "Disabled"}</dd>
            </div>
            <div>
              <dt>SSL</dt>
              <dd>{item.useSsl ? "Enabled" : "Disabled"}</dd>
            </div>
          </dl>
        ) : (
          <p>No SMTP credentials configured yet.</p>
        )}
      </section>

      {editing ? (
        <FormModal<SmtpFormValues>
          key={item ? "smtp-edit" : "smtp-create"}
          title={item ? "Edit SMTP credentials" : "Create SMTP credentials"}
          description="Provide the host, port, username, and password."
          initialValues={
            item
              ? {
                  host: item.host,
                  port: item.port,
                  username: item.username,
                  password: "",
                  senderEmail: item.senderEmail ?? "",
                  useTls: item.useTls,
                  useSsl: item.useSsl,
                }
              : defaultValues
          }
          fields={[
            { name: "host", label: "Host", required: true },
            { name: "port", label: "Port", type: "number", required: true },
            { name: "username", label: "Username", required: true },
            { name: "password", label: "Password", required: !item },
            { name: "senderEmail", label: "Sender email", type: "email" },
            { name: "useTls", label: "Use TLS", type: "checkbox" },
            { name: "useSsl", label: "Use SSL", type: "checkbox" },
          ]}
          submitLabel={item ? "Update credentials" : "Create credentials"}
          onSubmit={async (values) => {
            const payload = {
              host: values.host.trim(),
              port: Number(values.port),
              username: values.username.trim(),
              password: values.password,
              senderEmail: values.senderEmail.trim() || null,
              useTls: values.useTls,
              useSsl: values.useSsl,
            } satisfies SmtpCredentialCreateInput;

            if (item) {
              await updateMutation.mutateAsync(payload);
              return;
            }

            await createMutation.mutateAsync(payload);
          }}
          onClose={() => setEditing(false)}
        />
      ) : null}

      {viewOpen && item ? (
        <Modal
          title={item.secretName}
          description="SMTP credential details"
          onClose={() => setViewOpen(false)}
        >
          <dl className="lm-details">
            <div>
              <dt>Host</dt>
              <dd>{item.host}</dd>
            </div>
            <div>
              <dt>Port</dt>
              <dd>{item.port}</dd>
            </div>
            <div>
              <dt>Username</dt>
              <dd>{item.username}</dd>
            </div>
            <div>
              <dt>Sender email</dt>
              <dd>{item.senderEmail ?? "-"}</dd>
            </div>
          </dl>
        </Modal>
      ) : null}

      {deleteOpen ? (
        <ConfirmDialog
          title="Delete SMTP credentials"
          description="Delete the configured SMTP secret?"
          confirmLabel={
            deleteMutation.isPending ? "Deleting..." : "Delete credentials"
          }
          danger
          onClose={() => setDeleteOpen(false)}
          onConfirm={() => deleteMutation.mutate()}
        />
      ) : null}
    </PageContainer>
  );
}
