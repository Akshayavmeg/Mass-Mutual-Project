import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getAuditHistory } from "../api/cheques.js";
import { AuditTimeline } from "../components/cheque/AuditTimeline.jsx";
import { Card } from "../components/common/Card.jsx";
import { EmptyState, ErrorState, LoadingState } from "../components/common/States.jsx";
import { useApi } from "../hooks/useApi.js";

export default function AuditPage() {
  const { chequeId } = useParams();
  const navigate = useNavigate();
  const [searchValue, setSearchValue] = useState(chequeId ?? "");

  const { data, error, loading, refetch } = useApi(
    () => (chequeId ? getAuditHistory(chequeId) : Promise.resolve(null)),
    [chequeId],
  );

  function handleSearch(event) {
    event.preventDefault();
    if (searchValue.trim()) navigate(`/audit/${searchValue.trim()}`);
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Audit Trail</h1>
        <p className="text-sm text-slate-500">
          Look up the complete, append-only audit history for a specific cheque.
        </p>
      </div>

      <Card>
        <form className="flex gap-2" onSubmit={handleSearch}>
          <input
            type="text"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            placeholder="Enter a Cheque ID, e.g. CHK-2026-000001"
            className="flex-1 rounded-md border border-slate-300 px-3 py-1.5 text-sm focus:border-slate-500 focus:outline-none"
          />
          <button type="submit" className="rounded-md bg-slate-900 px-4 py-1.5 text-sm font-medium text-white hover:bg-slate-800">
            View Audit Trail
          </button>
        </form>
      </Card>

      {!chequeId && (
        <EmptyState title="No cheque selected" message="Enter a Cheque ID above, or open a cheque's Audit tab from its detail page." />
      )}

      {chequeId && loading && <LoadingState label="Loading audit history…" />}
      {chequeId && error && <ErrorState error={error} onRetry={refetch} />}
      {chequeId && data && (
        <Card title={`Audit History — ${chequeId}`}>
          <AuditTimeline events={data.events} />
        </Card>
      )}
    </div>
  );
}
