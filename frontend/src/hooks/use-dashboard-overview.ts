import { useQuery } from "@tanstack/react-query";
import type { ApiError } from "../api";
import { getDashboardOverview } from "../services";
import type { DashboardOverview } from "../types";
import { queryKeys } from "./query-keys";

export function useDashboardOverview() {
  return useQuery<DashboardOverview, ApiError>({
    queryKey: queryKeys.dashboard.overview(),
    queryFn: () => getDashboardOverview(),
  });
}
