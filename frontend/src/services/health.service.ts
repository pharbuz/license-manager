import { apiRequest } from "../api";
import type { HealthResponse } from "../types";

export function getHealth() {
  return apiRequest<HealthResponse>({
    method: "GET",
    url: "/health",
  });
}
