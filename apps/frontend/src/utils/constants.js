// Mirrors app/core/authorization.py's Role/Permission enums and
// permission matrix -- used ONLY to decide what to show/hide in the UI
// for convenience. The backend re-checks every mutating request
// server-side; this is never treated as the actual security boundary
// (see docs on ReviewQueuePage / UploadPage for how 401/403 responses
// are still handled even when a control is shown).
export const ROLES = ["ADMINISTRATOR", "OPERATOR", "REVIEWER", "AUDITOR", "SYSTEM_SERVICE"];

export const ROLE_LABELS = {
  ADMINISTRATOR: "Administrator",
  OPERATOR: "Operator",
  REVIEWER: "Reviewer",
  AUDITOR: "Auditor",
  SYSTEM_SERVICE: "System Service",
};

export const PERMISSION = {
  CHEQUE_UPLOAD: "CHEQUE_UPLOAD",
  CHEQUE_VIEW: "CHEQUE_VIEW",
  CHEQUE_PROCESS: "CHEQUE_PROCESS",
  REVIEW_VIEW: "REVIEW_VIEW",
  REVIEW_UPDATE: "REVIEW_UPDATE",
  DECISION_APPROVE: "DECISION_APPROVE",
  DECISION_REJECT: "DECISION_REJECT",
  AUDIT_VIEW: "AUDIT_VIEW",
};

const ROLE_PERMISSIONS = {
  ADMINISTRATOR: [PERMISSION.CHEQUE_VIEW, PERMISSION.AUDIT_VIEW, PERMISSION.REVIEW_VIEW],
  OPERATOR: [PERMISSION.CHEQUE_UPLOAD, PERMISSION.CHEQUE_VIEW, PERMISSION.CHEQUE_PROCESS],
  REVIEWER: [
    PERMISSION.CHEQUE_VIEW, PERMISSION.REVIEW_VIEW, PERMISSION.REVIEW_UPDATE,
    PERMISSION.DECISION_APPROVE, PERMISSION.DECISION_REJECT,
  ],
  AUDITOR: [PERMISSION.CHEQUE_VIEW, PERMISSION.AUDIT_VIEW],
  SYSTEM_SERVICE: [
    PERMISSION.CHEQUE_VIEW, PERMISSION.CHEQUE_PROCESS,
    PERMISSION.DECISION_APPROVE, PERMISSION.DECISION_REJECT,
  ],
};

export function roleHasPermission(role, permission) {
  return Boolean(role && ROLE_PERMISSIONS[role]?.includes(permission));
}

export const RISK_LEVEL_STYLES = {
  LOW: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  MEDIUM: "bg-amber-50 text-amber-700 ring-amber-600/20",
  HIGH: "bg-orange-50 text-orange-700 ring-orange-600/20",
  CRITICAL: "bg-red-50 text-red-700 ring-red-600/20",
};

export const DECISION_STYLES = {
  APPROVE: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  REVIEW: "bg-amber-50 text-amber-700 ring-amber-600/20",
  REJECT: "bg-red-50 text-red-700 ring-red-600/20",
};

export const STATUS_STYLES = {
  PASS: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  MATCH: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  APPROVED: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  WARNING: "bg-amber-50 text-amber-700 ring-amber-600/20",
  UNCERTAIN: "bg-amber-50 text-amber-700 ring-amber-600/20",
  NOT_AVAILABLE: "bg-slate-100 text-slate-600 ring-slate-500/20",
  NOT_CHECKED: "bg-slate-100 text-slate-600 ring-slate-500/20",
  UNAVAILABLE: "bg-slate-100 text-slate-600 ring-slate-500/20",
  FAIL: "bg-red-50 text-red-700 ring-red-600/20",
  MISMATCH: "bg-red-50 text-red-700 ring-red-600/20",
  REJECTED: "bg-red-50 text-red-700 ring-red-600/20",
};

export const PROCESSING_STAGES = [
  { key: "uploaded", label: "Uploaded", recordKey: null },
  { key: "preprocessed", label: "Preprocessed", recordKey: "preprocessing" },
  { key: "ocr", label: "OCR", recordKey: "ocr" },
  { key: "extraction", label: "Extraction", recordKey: "extraction" },
  { key: "validation", label: "Validation", recordKey: "validation" },
  { key: "fraud_analysis", label: "Fraud Analysis", recordKey: "fraud_analysis" },
  { key: "signature_analysis", label: "Signature Analysis", recordKey: "signature_analysis" },
  { key: "anomaly_analysis", label: "Anomaly Analysis", recordKey: "anomaly_analysis" },
  { key: "risk_assessment", label: "Risk Assessment", recordKey: "risk_assessment" },
  { key: "decision", label: "Decision", recordKey: "decision" },
];
