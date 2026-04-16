import { apiRequest } from "../api";
import type { DashboardOverview } from "../types";

export function getDashboardOverview() {
  return apiRequest<DashboardOverview>({
    method: "GET",
    url: "/dashboard",
  });
}
