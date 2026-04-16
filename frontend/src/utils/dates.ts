export function toDateTimeLocalValue(value: string | null | undefined) {
  if (!value) {
    return "";
  }

  return value.slice(0, 16);
}

export function toIsoDateTimeValue(value: string) {
  if (!value) {
    return value;
  }

  return new Date(value).toISOString();
}
