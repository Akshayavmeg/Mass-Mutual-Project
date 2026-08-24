import { getHealth } from "../api/client.js";
import { Badge } from "../components/common/Badge.jsx";
import { Card } from "../components/common/Card.jsx";
import { ErrorState, LoadingState } from "../components/common/States.jsx";
import { useApi } from "../hooks/useApi.js";

export default function SystemStatusPage() {
  const { data, error, loading, refetch } = useApi(() => getHealth(), []);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">System Status</h1>
        <p className="text-sm text-slate-500">Live status reported by the backend's health endpoint.</p>
      </div>

      {loading && <LoadingState label="Checking backend…" />}

      {error && (
        <Card title="Backend API">
          <div className="flex items-center gap-2">
            <Badge className="bg-red-50 text-red-700 ring-red-600/20">Unreachable</Badge>
          </div>
          <ErrorState error={error} onRetry={refetch} />
        </Card>
      )}

      {data && (
        <Card title="Backend API">
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div>
              <dt className="text-xs text-slate-500">Application Status</dt>
              <dd className="mt-1">
                <Badge
                  className={
                    data.status === "healthy"
                      ? "bg-emerald-50 text-emerald-700 ring-emerald-600/20"
                      : "bg-red-50 text-red-700 ring-red-600/20"
                  }
                >
                  {data.status}
                </Badge>
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500">Service</dt>
              <dd className="mt-1 text-sm font-medium text-slate-900">{data.service}</dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500">Database</dt>
              <dd className="mt-1">
                <Badge
                  className={
                    data.database === "connected"
                      ? "bg-emerald-50 text-emerald-700 ring-emerald-600/20"
                      : "bg-amber-50 text-amber-700 ring-amber-600/20"
                  }
                >
                  {data.database}
                </Badge>
              </dd>
            </div>
          </dl>
          {data.database !== "connected" && (
            <p className="mt-3 rounded-md bg-amber-50 p-3 text-xs text-amber-800">
              The database is not connected. The backend is running against its in-memory/CSV fallback
              repositories in this state (see the Milestone 8/9 reports) — processing still works, but results
              will not survive a backend restart.
            </p>
          )}
        </Card>
      )}
    </div>
  );
}
