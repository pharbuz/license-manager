import { apiRequest } from "../api";
import type {
  SmtpCredential,
  SmtpCredentialCreateInput,
  SmtpCredentialUpdateInput,
} from "../types";

export function getSmtpCredentials() {
  return apiRequest<SmtpCredential>({
    method: "GET",
    url: "/smtp-credentials",
  });
}

export function createSmtpCredentials(payload: SmtpCredentialCreateInput) {
  return apiRequest<SmtpCredential>({
    method: "POST",
    url: "/smtp-credentials",
    data: payload,
  });
}

export function updateSmtpCredentials(payload: SmtpCredentialUpdateInput) {
  return apiRequest<SmtpCredential>({
    method: "PUT",
    url: "/smtp-credentials",
    data: payload,
  });
}

export function deleteSmtpCredentials() {
  return apiRequest<void>({
    method: "DELETE",
    url: "/smtp-credentials",
  });
}
