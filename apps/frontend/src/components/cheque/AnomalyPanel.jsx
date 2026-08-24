import { Card } from "../common/Card.jsx";
import { RiskBadge, SeverityBadge } from "../common/Badge.jsx";
import { EmptyState } from "../common/States.jsx";
import { formatNumber, titleCase } from "../../utils/format.js";

export function AnomalyPanel({ anomaly }) {
  if (!anomaly) {
    return (
      <Card title="Anomaly Detection">
        <EmptyState title="Not run yet" message="Anomaly analysis has not been run for this cheque." />
      </Card>
    );
  }

  return (
    <Card
      title="Anomaly Detection"
      action={<RiskBadge level={anomaly.risk_level} />}
      subtitle={`${anomaly.model_name ?? "—"} ${anomaly.model_version ?? ""}`}
    >
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <div>
          <p className="text-xs text-slate-500">Anomaly Score</p>
          <p className="text-lg font-semibold text-slate-900">{formatNumber(anomaly.anomaly_score)}/100</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Analysis Status</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(anomaly.analysis_status)}</p>
        </div>
      </div>

      {anomaly.anomalies?.length > 0 ? (
        <div className="mt-4 space-y-2">
          <p className="text-xs font-medium uppercase text-slate-500">Detected Anomalies</p>
          {anomaly.anomalies.map((a, i) => (
            <div key={i} className="rounded-md border border-slate-200 p-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="font-medium text-slate-800">{titleCase(a.type)}</span>
                <SeverityBadge severity={a.severity} />
              </div>
              <p className="mt-1 text-slate-600">{a.reason}</p>
            </div>
          ))}
        </div>
      ) : (
        <p className="mt-4 text-sm text-slate-500">No anomalies were detected for this cheque.</p>
      )}

      {anomaly.unavailable_inputs?.length > 0 && (
        <p className="mt-3 text-xs italic text-slate-500">
          Unavailable inputs (not treated as normal): {anomaly.unavailable_inputs.join(", ")}
        </p>
      )}
    </Card>
  );
}
