import { useCallback, useEffect, useRef, useState } from "react";

/** Runs `fetcher()` whenever `deps` change, exposing {data, error,
 * loading, refetch}. Centralizes the loading/error/success state
 * machine every page needs so pages don't hand-roll it individually. */
export function useApi(fetcher, deps = []) {
  const [state, setState] = useState({ data: null, error: null, loading: true });
  const requestId = useRef(0);

  const run = useCallback(() => {
    const id = ++requestId.current;
    setState((prev) => ({ ...prev, loading: true, error: null }));
    fetcher()
      .then((data) => {
        if (id === requestId.current) setState({ data, error: null, loading: false });
      })
      .catch((error) => {
        if (id === requestId.current) setState({ data: null, error, loading: false });
      });
  }, deps); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  return { ...state, refetch: run };
}
