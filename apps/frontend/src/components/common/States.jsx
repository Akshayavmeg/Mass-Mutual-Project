export function LoadingState({ label = "Loading…" }) {
  return (
    <div className="flex items-center justify-center gap-3 py-12 text-sm text-slate-500" data-testid="loading-state">
      <span className="h-4 w-4 animate-spin rounded-full border-2 border-slate-300 border-t-slate-600" />
      {label}
    </div>
  );
}

export function ErrorState({ error, onRetry, label }) {
  const status = error?.status;
  let message = label || error?.message || "Something went wrong.";
  let title = "Unable to load data";
  if (status === 401) {
    title = "Sign-in required";
    message = "You need to select a role to access this page.";
  } else if (status === 403) {
    title = "Forbidden";
    message = "Your current role does not have permission to view this.";
  } else if (status === 404) {
    title = "Not found";
    message = error?.message || "The requested resource does not exist.";
  } else if (error?.name === "NetworkError") {
    title = "Backend unreachable";
    message = "Could not reach the backend service. Confirm it is running and reachable.";
  }

  return (
    <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800" data-testid="error-state">
      <p className="font-medium">{title}</p>
      <p className="mt-1 text-red-700">{message}</p>
      {error?.requestId && <p className="mt-1 text-xs text-red-500">Request ID: {error.requestId}</p>}
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 rounded-md bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700"
        >
          Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title = "Nothing here yet", message, action }) {
  return (
    <div className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-8 text-center" data-testid="empty-state">
      <p className="text-sm font-medium text-slate-700">{title}</p>
      {message && <p className="mt-1 text-sm text-slate-500">{message}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
