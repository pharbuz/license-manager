import type { ReactNode } from "react";
import { createPortal } from "react-dom";
import { useEffect } from "react";

type ModalProps = {
  title: string;
  description?: string;
  children: ReactNode;
  onClose: () => void;
};

export function Modal({ title, description, children, onClose }: ModalProps) {
  const isBrowser = typeof document !== "undefined";

  useEffect(() => {
    if (!isBrowser) {
      return;
    }

    const { overflow } = document.body.style;
    document.body.style.overflow = "hidden";

    return () => {
      document.body.style.overflow = overflow;
    };
  }, [isBrowser]);

  if (!isBrowser) {
    return null;
  }

  const portalRoot = document.body;

  return createPortal(
    <div className="lm-modal__backdrop" role="presentation" onClick={onClose}>
      <div
        className="lm-modal"
        role="dialog"
        aria-modal="true"
        aria-labelledby="lm-modal-title"
        aria-describedby={description ? "lm-modal-description" : undefined}
        onClick={(event) => event.stopPropagation()}
      >
        <header className="lm-modal__header">
          <div>
            <h2 id="lm-modal-title">{title}</h2>
            {description ? (
              <p id="lm-modal-description">{description}</p>
            ) : null}
          </div>
          <button type="button" className="lm-modal__close" onClick={onClose}>
            Close
          </button>
        </header>

        <div className="lm-modal__body">{children}</div>
      </div>
    </div>,
    portalRoot,
  );
}
