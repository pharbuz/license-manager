import { afterEach, describe, expect, it, vi } from "vitest";
import * as api from "../../api";
import { listDropdownItems } from "../../services/dropdown.service";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("dropdown.service", () => {
  it("loads dropdown options for a type", async () => {
    const apiRequestSpy = vi.spyOn(api, "apiRequest").mockResolvedValue([]);

    await listDropdownItems("license kind");

    expect(apiRequestSpy).toHaveBeenCalledWith({
      method: "GET",
      url: "/dropdown",
      params: { type: "license kind" },
    });
  });
});
