import type { AxiosResponse } from "axios";
import { afterEach, describe, expect, it, vi } from "vitest";
import {
  apiClient,
  apiRequest,
  normalizeAxiosError,
  serializeQueryParams,
} from "../../api";

afterEach(() => {
  vi.restoreAllMocks();
});

describe("http-client", () => {
  it("serializes typed query params and omits nullish values", () => {
    const query = serializeQueryParams({
      search: "acme",
      page: 2,
      size: 25,
      enabled: true,
      tags: ["x", "y"],
      from: new Date("2026-01-10T12:00:00.000Z"),
      skip: undefined,
      empty: null,
    });

    expect(query).toContain("search=acme");
    expect(query).toContain("page=2");
    expect(query).toContain("size=25");
    expect(query).toContain("enabled=true");
    expect(query).toContain("tags=x");
    expect(query).toContain("tags=y");
    expect(query).toContain("from=2026-01-10T12%3A00%3A00.000Z");
    expect(query).not.toContain("skip=");
    expect(query).not.toContain("empty=");
  });

  it("normalizes axios errors with response payload", () => {
    const normalized = normalizeAxiosError({
      isAxiosError: true,
      message: "Request failed with status code 422",
      code: "ERR_BAD_REQUEST",
      response: {
        status: 422,
        data: {
          message: "Validation failed",
          detail: [{ field: "email", msg: "Invalid" }],
        },
      },
    });

    expect(normalized).toEqual({
      message: "Validation failed",
      status: 422,
      code: "ERR_BAD_REQUEST",
      details: [{ field: "email", msg: "Invalid" }],
    });
  });

  it("returns response body in apiRequest helper", async () => {
    const requestSpy = vi.spyOn(apiClient, "request").mockResolvedValue({
      data: { status: "ok" },
    } as AxiosResponse<{ status: string }>);

    const result = await apiRequest<{ status: string }>({
      method: "GET",
      url: "/health",
    });

    expect(requestSpy).toHaveBeenCalledWith({
      method: "GET",
      url: "/health",
    });
    expect(result).toEqual({ status: "ok" });
  });
});
