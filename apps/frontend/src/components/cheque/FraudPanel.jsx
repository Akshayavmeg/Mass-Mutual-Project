import { Card } from "../common/Card.jsx";
import { RiskBadge, SeverityBadge } from "../common/Badge.jsx";
import { EmptyState } from "../common/States.jsx";
import { formatNumber, titleCase } from "../../utils/format.js";

export function FraudPanel({ fraud }) {
  if (!fraud) {
    return (
      <Card title="Fraud Analysis">
        <EmptyState title="Not run yet" message="Fraud analysis has not been run for this cheque." />
      </Card>
    );
  }

  const duplicate = fraud.duplicate_analysis ?? {};
  const image = fraud.image_analysis ?? {};

  return (
    <Card title="Fraud Analysis" action={<RiskBadge level={fraud.risk_level} />}>
      <div className="rounded-md bg-slate-50 p-3 text-xs text-slate-500">
        This is a computed fraud <strong>risk score</strong>, not a confirmed fraud verdict. Cheques flagged
        MEDIUM/HIGH/CRITICAL are routed to manual review or rejection per the Decision Engine's own rules — the
        score itself is not a final judgment.
      </div>

      <div className="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div>
          <p className="text-xs text-slate-500">Fraud Risk Score</p>
          <p className="text-lg font-semibold text-slate-900">{formatNumber(fraud.fraud_risk_score)}/100</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Image Tampering Score</p>
          <p className="text-lg font-semibold text-slate-900">{formatNumber(image.image_tampering_score)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Duplicate Status</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(duplicate.duplicate_status)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Model Prediction</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(fraud.model_prediction)}</p>
        </div>
      </div>

      {fraud.explanation?.length > 0 && (
        <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">
          {fraud.explanation.map((line, i) => (
            <li key={i}>{line}</li>
          ))}
        </ul>
      )}

      {fraud.indicators?.length > 0 && (
        <div className="mt-4">
          <p className="mb-2 text-xs font-medium uppercase text-slate-500">Indicators</p>
          <div className="space-y-2">
            {fraud.indicators.map((ind, i) => (
              <div key={i} className="rounded-md border border-slate-200 p-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium text-slate-800">{titleCase(ind.type)}</span>
                  <SeverityBadge severity={ind.severity} />
                </div>
                <p className="mt-1 text-slate-600">{ind.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {fraud.rule_violations?.length > 0 && (
        <div className="mt-4">
          <p className="mb-2 text-xs font-medium uppercase text-slate-500">Rule Violations</p>
          <ul className="space-y-1 text-sm text-slate-700">
            {fraud.rule_violations.map((rule) => (
              <li key={rule.rule_id}>
                <span className="font-mono text-xs text-slate-500">{rule.rule_id}</span> — {rule.description}
              </li>
            ))}
          </ul>
        </div>
      )}

      {fraud.unavailable_inputs?.length > 0 && (
        <p className="mt-3 text-xs italic text-slate-500">
          Unavailable inputs (not treated as pass): {fraud.unavailable_inputs.join(", ")}
        </p>
      )}
    </Card>
  );
}
