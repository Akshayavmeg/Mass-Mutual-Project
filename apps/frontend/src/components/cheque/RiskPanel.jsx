import { Card } from "../common/Card.jsx";
import { RiskBadge } from "../common/Badge.jsx";
import { EmptyState } from "../common/States.jsx";
import { formatNumber, titleCase } from "../../utils/format.js";

export function RiskPanel({ risk }) {
  if (!risk) {
    return (
      <Card title="Overall Risk Assessment">
        <EmptyState title="Not run yet" message="Risk scoring has not been run for this cheque." />
      </Card>
    );
  }

  return (
    <Card title="Overall Risk Assessment" action={<RiskBadge level={risk.risk_level} />} subtitle="Combines fraud, validation, signature, duplicate, anomaly and OCR signals — distinct from the Fraud Analysis score above.">
      <div className="flex items-baseline gap-2">
        <span className="text-2xl font-semibold text-slate-900">{formatNumber(risk.overall_risk_score)}</span>
        <span className="text-sm text-slate-500">/ 100</span>
      </div>

      {risk.risk_factors?.length > 0 && (
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-slate-500">
                <th className="py-2 pr-4">Factor</th>
                <th className="py-2 pr-4">Contribution</th>
                <th className="py-2 pr-4">Reason</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {risk.risk_factors.map((f) => (
                <tr key={f.factor}>
                  <td className="py-2 pr-4 font-medium text-slate-700">{titleCase(f.factor)}</td>
                  <td className="py-2 pr-4 text-slate-900">
                    {formatNumber(f.contribution)} / {formatNumber(f.max_contribution)}
                  </td>
                  <td className="py-2 pr-4 text-slate-600">{f.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {risk.hard_rules_triggered?.length > 0 && (
        <p className="mt-3 text-sm text-orange-700">Hard rules triggered: {risk.hard_rules_triggered.join(", ")}</p>
      )}
      {risk.unavailable_inputs?.length > 0 && (
        <p className="mt-3 text-xs italic text-slate-500">Unavailable inputs: {risk.unavailable_inputs.join(", ")}</p>
      )}
      <p className="mt-3 text-xs text-slate-400">Config version: {risk.config_version}</p>
    </Card>
  );
}
