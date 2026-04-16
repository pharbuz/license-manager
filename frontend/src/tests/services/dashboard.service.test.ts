import { afterEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api";
import { getDashboardOverview } from "../../services/dashboard.service";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("dashboard.service", () => {
  it("loads the aggregated dashboard endpoint", async () => {
    const apiRequestSpy = vi.spyOn(api, "apiRequest").mockResolvedValue({});

    await getDashboardOverview();

    expect(apiRequestSpy).toHaveBeenCalledWith({
      method: "GET",
      url: "/dashboard",
    });
  });
});
