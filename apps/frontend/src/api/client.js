// Minimal API client foundation. Domain-specific calls (cheque upload,
// review queue, dashboard, etc.) are added by the milestones that implement
// those features; this establishes the shared request path and base URL
// resolution only.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function getHealth() {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json();
}

export { API_BASE_URL };
