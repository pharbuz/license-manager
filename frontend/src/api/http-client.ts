import axios, {
  AxiosError,
  type AxiosInstance,
  type AxiosRequestConfig,
  type AxiosResponse,
} from "axios";

export type QueryPrimitive = string | number | boolean | Date;
export type QueryParamValue =
  | QueryPrimitive
  | QueryPrimitive[]
  | null
  | undefined;
export type QueryParams = Record<string, QueryParamValue>;

export type ApiError = {
  message: string;
  status: number | null;
  code: string;
  details?: unknown;
};

export function serializeQueryParams(params?: QueryParams): string {
  if (!params) {
    return "";
  }

  const searchParams = new URLSearchParams();

  for (const [key, rawValue] of Object.entries(params)) {
    if (rawValue === null || rawValue === undefined) {
      continue;
    }

    if (Array.isArray(rawValue)) {
      for (const value of rawValue) {
        searchParams.append(key, toQueryStringValue(value));
      }
      continue;
    }

    searchParams.append(key, toQueryStringValue(rawValue));
  }

  return searchParams.toString();
}

function toQueryStringValue(value: QueryPrimitive): string {
  if (value instanceof Date) {
    return value.toISOString();
  }

  return String(value);
}

export function normalizeAxiosError(error: unknown): ApiError {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{
      detail?: unknown;
      message?: string;
    }>;

    return {
      message:
        axiosError.response?.data?.message ??
        axiosError.message ??
        "Request failed.",
      status: axiosError.response?.status ?? null,
      code: axiosError.code ?? "REQUEST_ERROR",
      details: axiosError.response?.data?.detail,
    };
  }

  if (error instanceof Error) {
    return {
      message: error.message,
      status: null,
      code: "UNKNOWN_ERROR",
    };
  }

  return {
    message: "Unexpected error.",
    status: null,
    code: "UNKNOWN_ERROR",
    details: error,
  };
}

const baseURL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const apiClient: AxiosInstance = axios.create({
  baseURL,
  paramsSerializer: {
    serialize: (params) => serializeQueryParams(params as QueryParams),
  },
});

apiClient.interceptors.request.use((config) => {
  const headers = config.headers;
  headers.set("Accept", "application/json");

  if (config.data && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const token = localStorage.getItem("lm.accessToken");
  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return config;
});

apiClient.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: unknown) => Promise.reject(normalizeAxiosError(error)),
);

export async function apiRequest<TResponse>(
  config: AxiosRequestConfig,
): Promise<TResponse> {
  const response = await apiClient.request<TResponse>(config);
  return response.data;
}
