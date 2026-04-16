import { useState } from "react";
import type { FormEvent, ReactNode } from "react";
import { Modal } from "./Modal";

export type FormFieldType =
  | "text"
  | "email"
  | "number"
  | "checkbox"
  | "textarea"
  | "datetime-local";

export type FormFieldConfig<TValues extends Record<string, unknown>> = {
  name: keyof TValues & string;
  label: string;
  type?: FormFieldType;
  required?: boolean;
  placeholder?: string;
  helpText?: string;
};

type FormModalProps<TValues extends Record<string, unknown>> = {
  title: string;
  description?: string;
  fields: Array<FormFieldConfig<TValues>>;
  initialValues: TValues;
  submitLabel?: string;
  onSubmit: (values: TValues) => void | Promise<void>;
  onClose: () => void;
  footer?: ReactNode;
};

function normalizeFieldValue(value: unknown, type: FormFieldType) {
  if (type === "number") {
    return typeof value === "number" ? String(value) : String(value ?? "");
  }

  if (type === "checkbox") {
    return Boolean(value);
  }

  if (value === null || value === undefined) {
    return "";
  }

  if (type === "datetime-local" && typeof value === "string") {
    return value.slice(0, 16);
  }

  return String(value);
}

export function FormModal<TValues extends Record<string, unknown>>({
  title,
  description,
  fields,
  initialValues,
  submitLabel = "Save",
  onSubmit,
  onClose,
  footer,
}: FormModalProps<TValues>) {
  const [formValues, setFormValues] = useState<TValues>(initialValues);

  function updateField(name: keyof TValues & string, value: unknown) {
    setFormValues((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit(formValues);
  }

  return (
    <Modal title={title} description={description} onClose={onClose}>
      <form className="lm-form" onSubmit={handleSubmit}>
        {fields.map((field) => {
          const type = field.type ?? "text";
          const value = normalizeFieldValue(formValues[field.name], type);

          return (
            <label className="lm-form__field" key={field.name}>
              <span>{field.label}</span>
              {type === "textarea" ? (
                <textarea
                  value={String(value)}
                  placeholder={field.placeholder}
                  required={field.required}
                  onChange={(event) =>
                    updateField(field.name, event.target.value)
                  }
                />
              ) : type === "checkbox" ? (
                <input
                  type="checkbox"
                  checked={Boolean(value)}
                  onChange={(event) =>
                    updateField(field.name, event.target.checked)
                  }
                />
              ) : (
                <input
                  type={type}
                  value={String(value)}
                  placeholder={field.placeholder}
                  required={field.required}
                  onChange={(event) => {
                    const nextValue =
                      type === "number"
                        ? event.target.value === ""
                          ? ""
                          : Number(event.target.value)
                        : event.target.value;
                    updateField(field.name, nextValue);
                  }}
                />
              )}
              {field.helpText ? <small>{field.helpText}</small> : null}
            </label>
          );
        })}

        <div className="lm-form__footer">
          {footer}
          <button type="submit" className="lm-button lm-button--primary">
            {submitLabel}
          </button>
        </div>
      </form>
    </Modal>
  );
}
