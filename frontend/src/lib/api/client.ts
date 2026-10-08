import type { ApiErrorBody } from "./types";

/** A failed API call. `code` is the API's stable error code, or "network_error" if it was never reached. */
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Calls the backend through this site's /api proxy (see next.config.ts) and returns the parsed JSON.
 * Every non-2xx response is turned into an ApiError carrying the API's error code.
 */
export async function apiFetch<T>(path: string, init: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api/v1${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init.headers },
    });
  } catch {
    throw new ApiError(0, "network_error", "Can't reach the server. Check your connection and try again.");
  }

  const body: unknown = await response.json().catch(() => null);
  if (!response.ok) {
    const error = (body as ApiErrorBody | null)?.error;
    throw new ApiError(response.status, error?.code ?? "http_error", error?.message ?? response.statusText);
  }
  return body as T;
}
