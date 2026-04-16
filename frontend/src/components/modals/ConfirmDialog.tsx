import { Modal } from "./Modal";

type ConfirmDialogProps = {
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean;
  onConfirm: () => void;
  onClose: () => void;
};

export function ConfirmDialog({
  title,
  description,
  confirmLabel = "Confirm",
  cancelLabel = "Cancel",
  danger = false,
  onConfirm,
  onClose,
}: ConfirmDialogProps) {
  return (
    <Modal title={title} description={description} onClose={onClose}>
      <div className="lm-confirm">
        <div className="lm-confirm__actions">
          <button type="button" className="lm-button" onClick={onClose}>
            {cancelLabel}
          </button>
          <button
            type="button"
            className={danger ? "lm-button lm-button--danger" : "lm-button"}
            onClick={onConfirm}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </Modal>
  );
}
