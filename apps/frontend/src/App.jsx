import { useEffect, useState } from "react";
import { getHealth } from "./api/client.js";

export default function App() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;

    getHealth()
      .then((data) => {
        if (!cancelled) setHealth(data);
      })
      .catch((err) => {
        if (!cancelled) setError(err.message);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <main className="min-h-screen bg-slate-50 flex items-center justify-center p-6">
      <div className="max-w-md w-full rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <h1 className="text-lg font-semibold text-slate-900">
          Mass Mutual Cheque Fraud Detection System
        </h1>
        <p className="mt-1 text-sm text-slate-500">Development foundation status</p>

        <div className="mt-4 rounded-md bg-slate-50 p-4 text-sm">
          {error && (
            <p className="text-red-600" data-testid="backend-status-error">
              Unable to reach backend: {error}
            </p>
          )}
          {!error && !health && <p data-testid="backend-status-loading">Checking backend...</p>}
          {health && (
            <dl className="space-y-1" data-testid="backend-status-ok">
              <div className="flex justify-between">
                <dt className="text-slate-500">Backend status</dt>
                <dd className="font-medium text-slate-900">{health.status}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Service</dt>
                <dd className="font-medium text-slate-900">{health.service}</dd>
              </div>
              <div className="flex justify-between">
                <dt className="text-slate-500">Database</dt>
                <dd className="font-medium text-slate-900">{health.database}</dd>
              </div>
            </dl>
          )}
        </div>
      </div>
    </main>
  );
}
