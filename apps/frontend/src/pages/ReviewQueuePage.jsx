import { Link, useSearchParams } from "react-router-dom";
import { getReviewQueue } from "../api/reviews.js";
import { Badge, RiskBadge, SeverityBadge, StatusBadge } from "../components/common/Badge.jsx";
import { Card } from "../components/common/Card.jsx";
import { EmptyState, ErrorState, LoadingState } from "../components/common/States.jsx";
import { useApi } from "../hooks/useApi.js";
import { formatCurrency, formatDate } from "../utils/format.js";

const STATUS_OPTIONS = ["", "QUEUED", "ASSIGNED", "UNDER_REVIEW", "ESCALATED", "CLOSED"];
const PRIORITY_OPTIONS = ["", "CRITICAL", "HIGH", "MEDIUM", "LOW"];

export default function ReviewQueuePage() {
  const [params, setParams] = useSearchParams();
  const status = params.get("status") || "";
  const priority = params.get("priority") || "";

  const { data, error, loading, refetch } = useApi(() => getReviewQueue({ status, priority }), [status, priority]);

  function updateParam(key, value) {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next);
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Manual Review Queue</h1>
        <p className="text-sm text-slate-500">Cheques the Decision Engine routed to human review.</p>
      </div>

      <Card>
        <div className="flex flex-wrap gap-3">
          <select
            value={status}
            onChange={(e) => updateParam("status", e.target.value)}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
          >
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>
                {s || "All statuses"}
              </option>
            ))}
          </select>
          <select
            value={priority}
            onChange={(e) => updateParam("priority", e.target.value)}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
          >
            {PRIORITY_OPTIONS.map((p) => (
              <option key={p} value={p}>
                {p || "All priorities"}
              </option>
            ))}
          </select>
        </div>
      </Card>

      {loading ? (
        <LoadingState label="Loading review queue…" />
      ) : error ? (
        <ErrorState error={error} onRetry={refetch} />
      ) : data.cases.length === 0 ? (
        <EmptyState title="Queue is empty" message="No review cases match the current filters." />
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead>
                <tr className="text-left text-xs uppercase text-slate-500">
                  <th className="py-2 pr-4">Review Case</th>
                  <th className="py-2 pr-4">Cheque</th>
                  <th className="py-2 pr-4">Amount</th>
                  <th className="py-2 pr-4">Priority</th>
                  <th className="py-2 pr-4">Risk</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">Assigned</th>
                  <th className="py-2 pr-4">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.cases.map((c) => (
                  <tr key={c.review_case_id} className="hover:bg-slate-50">
                    <td className="py-2 pr-4">
                      <Link to={`/reviews/${c.review_case_id}`} className="font-mono text-xs text-slate-900 hover:underline">
                        {c.review_case_id}
                      </Link>
                    </td>
                    <td className="py-2 pr-4 font-mono text-xs text-slate-600">{c.cheque_id}</td>
                    <td className="py-2 pr-4 text-slate-700">{formatCurrency(c.cheque_summary?.amount)}</td>
                    <td className="py-2 pr-4">
                      <SeverityBadge severity={c.priority} />
                    </td>
                    <td className="py-2 pr-4">
                      <RiskBadge level={c.risk_level} />
                    </td>
                    <td className="py-2 pr-4">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="py-2 pr-4 text-slate-600">
                      {c.assigned_reviewer_id ? c.assigned_reviewer_id : <Badge>Unassigned</Badge>}
                    </td>
                    <td className="py-2 pr-4 whitespace-nowrap text-slate-500">{formatDate(c.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
