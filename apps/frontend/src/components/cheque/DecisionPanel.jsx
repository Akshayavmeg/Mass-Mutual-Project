import { Card } from "../common/Card.jsx";
import { DecisionBadge } from "../common/Badge.jsx";
import { EmptyState } from "../common/States.jsx";
import { formatDate, titleCase } from "../../utils/format.js";

export function DecisionPanel({ decision, humanDecision }) {
  if (!decision) {
    return (
      <Card title="Decision">
        <EmptyState title="Not decided yet" message="The Decision Engine has not run for this cheque." />
      </Card>
    );
  }

  const evidence = decision.evidence ?? {};

  return (
    <Card title="Decision" action={<DecisionBadge decision={decision.decision} />}>
      <p className="text-sm font-medium text-slate-900">{decision.decision_reason}</p>
      {decision.reasons?.length > 1 && (
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
          {decision.reasons.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      )}

      <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-3">
        <div>
          <p className="text-xs text-slate-500">Validation</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(evidence.validation_status)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Fraud Risk</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(evidence.fraud_risk_level)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Signature Risk</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(evidence.signature_risk_level)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Anomaly Risk</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(evidence.anomaly_risk_level)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Duplicate Status</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(evidence.duplicate_status)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Overall Risk</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(evidence.overall_risk_level)}</p>
        </div>
      </div>

      {decision.triggered_rules?.length > 0 && (
        <p className="mt-3 text-sm text-slate-700">
          Triggered rules: <span className="font-mono text-xs">{decision.triggered_rules.join(", ")}</span>
        </p>
      )}
      {decision.escalation_reason && (
        <p className="mt-2 rounded-md bg-amber-50 p-2 text-sm text-amber-800">
          Escalation reason: {decision.escalation_reason}
        </p>
      )}

      <p className="mt-3 text-xs text-slate-400">
        Policy {decision.policy_version} · Ruleset {decision.ruleset_version} · {formatDate(decision.decision_timestamp)}
      </p>

      {humanDecision && (
        <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3">
          <p className="text-xs font-medium uppercase text-slate-500">Human Review Decision</p>
          <p className="mt-1 text-sm font-medium text-slate-900">
            {humanDecision.decision} by {humanDecision.reviewer_id}
          </p>
          <p className="mt-1 text-sm text-slate-600">{humanDecision.comment}</p>
          <p className="mt-1 text-xs text-slate-400">{formatDate(humanDecision.timestamp)}</p>
        </div>
      )}
    </Card>
  );
}
