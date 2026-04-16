import { apiRequest } from "../api";
import type { AuditLogEntry, AuditLogListQuery } from "../types";

export function listAuditLogs(params?: AuditLogListQuery) {
  const {
    entityType,
    entityId,
    requestId,
    actorId,
    source,
    occurredFrom,
    occurredTo,
  } = params ?? {};

  return apiRequest<AuditLogEntry[]>({
    method: "GET",
    url: "/audit/logs",
    params: {
      entityType,
      entityId,
      requestId,
      actorId,
      source,
      occurredFrom,
      occurredTo,
    },
  });
}
