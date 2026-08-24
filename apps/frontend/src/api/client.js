// Central HTTP layer. Every API call in the app goes through `request()`
// so headers (dev-mode role context), error-envelope parsing, and
// network-failure handling are implemented exactly once.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message, { status, code, requestId } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status ?? null;
    this.code = code ?? null;
    this.requestId = requestId ?? null;
  }
}

export class NetworkError extends Error {
  constructor(message) {
    super(message);
    this.name = "NetworkError";
  }
}

let currentUser = { role: null, userId: null };

/** Sets the dev-mode role context (see src/context/UserContext.jsx) that
 * every subsequent request sends via X-User-Role / X-User-Id -- the
 * documented development user-context mechanism this milestone's
 * instructions call for in place of full JWT login. */
export function setRequestUserContext({ role, userId }) {
  currentUser = { role: role ?? null, userId: userId ?? null };
}

function buildHeaders(extra = {}) {
  const headers = { ...extra };
  if (currentUser.role) headers["X-User-Role"] = currentUser.role;
  if (currentUser.userId) headers["X-User-Id"] = currentUser.userId;
  return headers;
}

async function parseErrorEnvelope(response) {
  try {
    const body = await response.json();
    if (body && body.error) {
      return new ApiError(body.error.message || "Request failed", {
        status: response.status,
        code: body.error.code,
        requestId: body.error.request_id,
      });
    }
    if (body && body.detail) {
      return new ApiError(String(body.detail), { status: response.status });
    }
  } catch {
    // response body wasn't JSON (or was empty) -- fall through
  }
  return new ApiError(`Request failed with status ${response.status}`, { status: response.status });
}

/**
 * @param {string} path - path relative to /api/v1 (must start with "/")
 * @param {object} [options]
 * @param {string} [options.method]
 * @param {object} [options.body] - JSON-serializable request body
 * @param {object} [options.headers]
 * @param {URLSearchParams|Record<string,string>} [options.query]
 * @param {boolean} [options.raw] - if true, returns the Response instead of parsed JSON
 */
export async function request(path, options = {}) {
  const { method = "GET", body, headers, query, raw = false, formData } = options;

  let url = `${API_BASE_URL}/api/v1${path}`;
  if (query) {
    const params = query instanceof URLSearchParams ? query : new URLSearchParams(query);
    // Drop empty/undefined filter values rather than sending "status="
    for (const key of [...params.keys()]) {
      if (params.get(key) === "" || params.get(key) === "undefined" || params.get(key) === "null") {
        params.delete(key);
      }
    }
    const qs = params.toString();
    if (qs) url += `?${qs}`;
  }

  const init = { method, headers: buildHeaders(headers) };
  if (formData) {
    init.body = formData; // let the browser set the multipart boundary
  } else if (body !== undefined) {
    init.body = JSON.stringify(body);
    init.headers["Content-Type"] = "application/json";
  }

  let response;
  try {
    response = await fetch(url, init);
  } catch (err) {
    throw new NetworkError(err?.message || "Unable to reach the backend service.");
  }

  if (!response.ok) {
    throw await parseErrorEnvelope(response);
  }

  if (raw) return response;
  if (response.status === 204) return null;
  return response.json();
}

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new ApiError(`Health check failed with status ${response.status}`, { status: response.status });
  }
  return response.json();
}

export function imageUrl(chequeId, variant) {
  return `${API_BASE_URL}/api/v1/cheques/${encodeURIComponent(chequeId)}/image/${variant}`;
}

export { API_BASE_URL };
