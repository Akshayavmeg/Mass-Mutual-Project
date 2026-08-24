import { useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { listCheques } from "../api/cheques.js";
import { DecisionBadge, RiskBadge, StatusBadge } from "../components/common/Badge.jsx";
import { Card } from "../components/common/Card.jsx";
import { EmptyState, ErrorState, LoadingState } from "../components/common/States.jsx";
import { useApi } from "../hooks/useApi.js";
import { formatCurrency, formatDate } from "../utils/format.js";

const STATUS_OPTIONS = [
  "", "UPLOADED", "PROCESSING", "OCR_COMPLETED", "RISK_SCORED", "DECISION_MADE",
  "UNDER_REVIEW", "APPROVED", "REJECTED", "FAILED",
];
const RISK_OPTIONS = ["", "LOW", "MEDIUM", "HIGH", "CRITICAL"];

export default function ChequeHistoryPage() {
  const [params, setParams] = useSearchParams();
  const [searchText, setSearchText] = useState("");
  const page = Number(params.get("page") || 1);
  const status = params.get("status") || "";
  const riskLevel = params.get("risk_level") || "";

  const { data, error, loading, refetch } = useApi(
    () => listCheques({ page, limit: 20, status, riskLevel }),
    [page, status, riskLevel],
  );

  const filtered = useMemo(() => {
    if (!data) return [];
    if (!searchText.trim()) return data.cheques;
    const needle = searchText.trim().toLowerCase();
    return data.cheques.filter(
      (c) => c.cheque_id.toLowerCase().includes(needle) || (c.payee_name ?? "").toLowerCase().includes(needle),
    );
  }, [data, searchText]);

  function updateParam(key, value) {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    next.set("page", "1");
    setParams(next);
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Cheques / History</h1>
        <p className="text-sm text-slate-500">Persisted cheque records retrieved from the backend.</p>
      </div>

      <Card>
        <div className="flex flex-wrap gap-3">
          <input
            type="text"
            placeholder="Search this page by Cheque ID or payee…"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            className="flex-1 min-w-[200px] rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-slate-500 focus:outline-none"
          />
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
            value={riskLevel}
            onChange={(e) => updateParam("risk_level", e.target.value)}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
          >
            {RISK_OPTIONS.map((r) => (
              <option key={r} value={r}>
                {r || "All risk levels"}
              </option>
            ))}
          </select>
        </div>
      </Card>

      {loading ? (
        <LoadingState label="Loading cheques…" />
      ) : error ? (
        <ErrorState error={error} onRetry={refetch} />
      ) : filtered.length === 0 ? (
        <EmptyState title="No cheques found" message="Try adjusting your filters, or upload a cheque to get started." />
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 text-sm">
              <thead>
                <tr className="text-left text-xs uppercase text-slate-500">
                  <th className="py-2 pr-4">Cheque ID</th>
                  <th className="py-2 pr-4">Payee</th>
                  <th className="py-2 pr-4">Amount</th>
                  <th className="py-2 pr-4">Status</th>
                  <th className="py-2 pr-4">Risk</th>
                  <th className="py-2 pr-4">Decision</th>
                  <th className="py-2 pr-4">Uploaded</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((c) => (
                  <tr key={c.cheque_id} className="hover:bg-slate-50">
                    <td className="py-2 pr-4">
                      <Link to={`/cheques/${c.cheque_id}`} className="font-mono text-xs text-slate-900 hover:underline">
                        {c.cheque_id}
                      </Link>
                    </td>
                    <td className="py-2 pr-4 text-slate-700">{c.payee_name ?? "—"}</td>
                    <td className="py-2 pr-4 text-slate-700">{formatCurrency(c.amount)}</td>
                    <td className="py-2 pr-4">
                      <StatusBadge status={c.status} />
                    </td>
                    <td className="py-2 pr-4">
                      <RiskBadge level={c.risk_level} />
                    </td>
                    <td className="py-2 pr-4">
                      <DecisionBadge decision={c.decision} />
                    </td>
                    <td className="py-2 pr-4 whitespace-nowrap text-slate-500">{formatDate(c.upload_timestamp)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between text-sm text-slate-500">
            <span>
              Page {data.page} · {data.total} total cheque{data.total === 1 ? "" : "s"}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() => updateParam("page", String(page - 1))}
                className="rounded-md border border-slate-300 px-3 py-1 disabled:opacity-40"
              >
                Previous
              </button>
              <button
                type="button"
                disabled={page * 20 >= data.total}
                onClick={() => updateParam("page", String(page + 1))}
                className="rounded-md border border-slate-300 px-3 py-1 disabled:opacity-40"
              >
                Next
              </button>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
