import { apiRequest } from "../api";
import type {
  License,
  LicenseCreateInput,
  LicenseGeneratedKey,
  LicenseGenerateInput,
  LicenseUpdateInput,
  Uuid,
} from "../types";

export function listLicenses() {
  return apiRequest<License[]>({
    method: "GET",
    url: "/licenses",
  });
}

export function listArchivedLicenses() {
  return apiRequest<License[]>({
    method: "GET",
    url: "/licenses/archive",
  });
}

export function listLicensesByCustomer(customerId: Uuid) {
  return apiRequest<License[]>({
    method: "GET",
    url: `/licenses/customer/${customerId}`,
  });
}

export function getLicense(licenseId: Uuid) {
  return apiRequest<License>({
    method: "GET",
    url: `/licenses/${licenseId}`,
  });
}

export function createLicense(payload: LicenseCreateInput) {
  return apiRequest<License>({
    method: "POST",
    url: "/licenses",
    data: payload,
  });
}

export function updateLicense(licenseId: Uuid, payload: LicenseUpdateInput) {
  return apiRequest<License>({
    method: "PATCH",
    url: `/licenses/${licenseId}`,
    data: payload,
  });
}

export function deleteLicense(licenseId: Uuid) {
  return apiRequest<void>({
    method: "DELETE",
    url: `/licenses/${licenseId}`,
  });
}

export function deleteLicenseViaGet(licenseId: Uuid) {
  return apiRequest<void>({
    method: "GET",
    url: `/licenses/${licenseId}/delete`,
  });
}

export function archiveLicense(licenseId: Uuid) {
  return apiRequest<License>({
    method: "GET",
    url: `/licenses/${licenseId}/archive`,
  });
}

export function unarchiveLicense(licenseId: Uuid) {
  return apiRequest<License>({
    method: "GET",
    url: `/licenses/${licenseId}/unarchive`,
  });
}

export function generateLicense(payload: LicenseGenerateInput) {
  return apiRequest<LicenseGeneratedKey>({
    method: "POST",
    url: "/licenses/generate",
    data: payload,
  });
}
