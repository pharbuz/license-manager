import { apiRequest } from "../api";
import type { DropdownItem, DropdownType } from "../types";

export function listDropdownItems(type: DropdownType) {
  return apiRequest<DropdownItem[]>({
    method: "GET",
    url: "/dropdown",
    params: { type },
  });
}
