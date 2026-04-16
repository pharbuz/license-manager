import { apiRequest } from "../api";
import type { Kind, KindCreateInput, KindUpdateInput, Uuid } from "../types";

export function listKinds() {
  return apiRequest<Kind[]>({
    method: "GET",
    url: "/kinds",
  });
}

export function getKind(kindId: Uuid) {
  return apiRequest<Kind>({
    method: "GET",
    url: `/kinds/${kindId}`,
  });
}

export function createKind(payload: KindCreateInput) {
  return apiRequest<Kind>({
    method: "POST",
    url: "/kinds",
    data: payload,
  });
}

export function updateKind(kindId: Uuid, payload: KindUpdateInput) {
  return apiRequest<Kind>({
    method: "PATCH",
    url: `/kinds/${kindId}`,
    data: payload,
  });
}

export function deleteKind(kindId: Uuid) {
  return apiRequest<void>({
    method: "DELETE",
    url: `/kinds/${kindId}`,
  });
}
