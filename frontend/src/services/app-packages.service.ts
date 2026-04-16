import { apiRequest, apiClient } from "../api";
import type {
  AppPackage,
  AppPackageCreateInput,
  AppPackageUpdateInput,
  Uuid,
} from "../types";

export function listAppPackages() {
  return apiRequest<AppPackage[]>({
    method: "GET",
    url: "/app-packages",
  });
}

export function getAppPackage(appPackageId: Uuid) {
  return apiRequest<AppPackage>({
    method: "GET",
    url: `/app-packages/${appPackageId}`,
  });
}

export function createAppPackage(payload: AppPackageCreateInput) {
  return apiRequest<AppPackage>({
    method: "POST",
    url: "/app-packages",
    data: payload,
  });
}

export function updateAppPackage(
  appPackageId: Uuid,
  payload: AppPackageUpdateInput,
) {
  return apiRequest<AppPackage>({
    method: "PATCH",
    url: `/app-packages/${appPackageId}`,
    data: payload,
  });
}

export function deleteAppPackage(appPackageId: Uuid) {
  return apiRequest<void>({
    method: "DELETE",
    url: `/app-packages/${appPackageId}`,
  });
}

export function deleteAppPackageViaGet(appPackageId: Uuid) {
  return apiRequest<void>({
    method: "GET",
    url: `/app-packages/${appPackageId}/delete`,
  });
}

export async function downloadAppPackage(appPackageId: Uuid, filePath: string) {
  const response = await apiClient.get<Blob>(
    `/app-packages/${appPackageId}/download`,
    {
      params: { filePath },
      responseType: "blob",
    },
  );

  return response.data;
}

export function notifyAppPackage(appPackageId: Uuid, versionId: Uuid) {
  return apiRequest<void>({
    method: "GET",
    url: `/app-packages/${appPackageId}/notify`,
    params: { versionId },
  });
}
