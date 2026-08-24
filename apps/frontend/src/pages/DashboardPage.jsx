import { useMemo } from "react";
import { getDashboardSummary, getFraudStatistics, getProcessingStatistics } from "../api/dashboard.js";
import { BarList } from "../components/common/BarList.jsx";
import { Card, StatCard } from "../components/common/Card.jsx";
import { ErrorState, LoadingState } from "../components/common/States.jsx";
import { useApi } from "../hooks/useApi.js";
import { formatPercent, formatSeconds } from "../utils/format.js";

async function loadAll() {
  const [summary, fraudStats, processingStats] = await Promise.all([
    getDashboardSummary(),
    getFraudStatistics(),
    getProcessingStatistics(),
  ]);
  return { summary, fraudStats, processingStats };
}

export default function DashboardPage() {
  const { data, error, loading, refetch } = useApi(loadAll, []);

  const riskItems = useMemo(() => {
    if (!data) return [];
    const f = data.fraudStats;
    return [
      { label: "Low", value: f.low_risk, colorClass: "bg-emerald-500" },
      { label: "Medium", value: f.medium_risk, colorClass: "bg-amber-500" },
      { label: "High", value: f.high_risk, colorClass: "bg-orange-500" },
      { label: "Critical", value: f.critical_risk, colorClass: "bg-red-500" },
    ];
  }, [data]);

  const decisionItems = useMemo(() => {
    if (!data) return [];
    const s = data.summary;
    return [
      { label: "Approved", value: s.approved, colorClass: "bg-emerald-500" },
      { label: "Review", value: s.under_review, colorClass: "bg-amber-500" },
      { label: "Rejected", value: s.rejected, colorClass: "bg-red-500" },
    ];
  }, [data]);

  if (loading) return <LoadingState label="Loading dashboard…" />;
  if (error) return <ErrorState error={error} onRetry={refetch} />;

  const { summary, processingStats } = data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500">
          Live metrics computed from persisted cheque records. This deployment uses synthetic/demo data only.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        <StatCard label="Total Cheques" value={summary.total_cheques} to="/cheques" />
        <StatCard label="Approved" value={summary.approved} to="/cheques?status=APPROVED" />
        <StatCard label="Under Review" value={summary.under_review} to="/reviews" />
        <StatCard label="Rejected" value={summary.rejected} to="/cheques?status=REJECTED" />
        <StatCard label="Fraud Alerts" value={summary.fraud_detected} hint="HIGH / CRITICAL fraud risk" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Decision Distribution">
          {decisionItems.every((i) => i.value === 0) ? (
            <p className="text-sm text-slate-500">No decisions recorded yet.</p>
          ) : (
            <BarList items={decisionItems} />
          )}
        </Card>
        <Card title="Fraud / Risk Distribution" subtitle="Overall risk level across all cheques">
          {riskItems.every((i) => i.value === 0) ? (
            <p className="text-sm text-slate-500">No risk assessments recorded yet.</p>
          ) : (
            <BarList items={riskItems} />
          )}
        </Card>
      </div>

      <Card title="Processing Statistics">
        <dl className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div>
            <dt className="text-xs text-slate-500">Avg. Processing Time</dt>
            <dd className="mt-1 text-lg font-semibold text-slate-900">
              {formatSeconds(processingStats.average_processing_time)}
            </dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">OCR Success Rate</dt>
            <dd className="mt-1 text-lg font-semibold text-slate-900">{formatPercent(processingStats.ocr_success_rate)}</dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Validation Success Rate</dt>
            <dd className="mt-1 text-lg font-semibold text-slate-900">
              {formatPercent(processingStats.validation_success_rate)}
            </dd>
          </div>
          <div>
            <dt className="text-xs text-slate-500">Manual Review Rate</dt>
            <dd className="mt-1 text-lg font-semibold text-slate-900">{formatPercent(processingStats.manual_review_rate)}</dd>
          </div>
        </dl>
        <p className="mt-3 text-xs text-slate-500">
          Average OCR confidence: {formatPercent(summary.average_ocr_confidence)}. These are measured values from
          this deployment's own processed cheques, not documentation targets.
        </p>
      </Card>
    </div>
  );
}
