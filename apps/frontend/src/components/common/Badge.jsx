import { DECISION_STYLES, RISK_LEVEL_STYLES, STATUS_STYLES } from "../../utils/constants.js";

const DEFAULT_STYLE = "bg-slate-100 text-slate-600 ring-slate-500/20";

export function Badge({ children, className = "" }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset ${className || DEFAULT_STYLE}`}
    >
      {children}
    </span>
  );
}

export function RiskBadge({ level }) {
  if (!level) return <Badge>Unavailable</Badge>;
  return <Badge className={RISK_LEVEL_STYLES[level] || DEFAULT_STYLE}>{level}</Badge>;
}

export function DecisionBadge({ decision }) {
  if (!decision) return <Badge>Pending</Badge>;
  return <Badge className={DECISION_STYLES[decision] || DEFAULT_STYLE}>{decision}</Badge>;
}

export function StatusBadge({ status }) {
  if (!status) return <Badge>—</Badge>;
  return <Badge className={STATUS_STYLES[status] || DEFAULT_STYLE}>{status.replace(/_/g, " ")}</Badge>;
}

export function SeverityBadge({ severity }) {
  const styles = {
    LOW: "bg-slate-100 text-slate-600 ring-slate-500/20",
    MEDIUM: "bg-amber-50 text-amber-700 ring-amber-600/20",
    HIGH: "bg-orange-50 text-orange-700 ring-orange-600/20",
    CRITICAL: "bg-red-50 text-red-700 ring-red-600/20",
  };
  return <Badge className={styles[severity] || DEFAULT_STYLE}>{severity || "—"}</Badge>;
}
