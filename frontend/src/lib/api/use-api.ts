import { useCallback, useEffect, useState } from "react";

import { ApiError } from "./client";

export type ApiState<T> =
  | { status: "loading" }
  | { status: "success"; data: T }
  | { status: "error"; error: ApiError };

/**
 * Loads data from the API when the component mounts. `load` must be stable.
 * `retry` shows the loading state again; `refresh` reloads quietly, keeping the current data on screen.
 */
export function useApi<T>(load: () => Promise<T>): ApiState<T> & { retry: () => void; refresh: () => Promise<void> } {
  const [state, setState] = useState<ApiState<T>>({ status: "loading" });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    load().then(
      (data) => {
        if (!cancelled) setState({ status: "success", data });
      },
      (error: unknown) => {
        if (cancelled) return;
        const apiError = error instanceof ApiError ? error : new ApiError(0, "unknown_error", String(error));
        setState({ status: "error", error: apiError });
      },
    );
    return () => {
      cancelled = true;
    };
  }, [load, attempt]);

  const retry = useCallback(() => {
    setState({ status: "loading" });
    setAttempt((count) => count + 1);
  }, []);

  const refresh = useCallback(async () => {
    const data = await load();
    setState({ status: "success", data });
  }, [load]);

  return { ...state, retry, refresh };
}
