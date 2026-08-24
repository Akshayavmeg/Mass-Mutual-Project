import { Card } from "../common/Card.jsx";
import { RiskBadge } from "../common/Badge.jsx";
import { EmptyState } from "../common/States.jsx";
import { formatPercent, titleCase } from "../../utils/format.js";

const INDICATOR_EXPLANATIONS = {
  SIGNATURE_MISSING: "No signature was detected in the signature region of the cheque.",
  SIGNATURE_MISMATCH: "The signature does not sufficiently match the account's reference signature.",
  SIGNATURE_ANALYSIS_UNRELIABLE: "The comparison result is not reliable enough to trust on its own.",
  INSUFFICIENT_IMAGE: "The signature image did not contain enough usable ink/detail to analyze.",
  SIGNATURE_IMAGE_LOW_QUALITY: "The signature image is blurred or low quality — a result is provided, but with reduced confidence.",
  REFERENCE_SIGNATURE_NOT_FOUND:
    "No authorized reference signature is on file for this account. This means verification could not be performed — it is NOT evidence of fraud.",
  SIGNATURE_ANALYSIS_ERROR: "An internal error prevented signature analysis from completing.",
  UNSUPPORTED_SIGNATURE_IMAGE: "The signature image format/content could not be processed.",
};

export function SignaturePanel({ signature }) {
  if (!signature) {
    return (
      <Card title="Signature Analysis">
        <EmptyState title="Not run yet" message="Signature analysis has not been run for this cheque." />
      </Card>
    );
  }

  return (
    <Card title="Signature Analysis" action={<RiskBadge level={signature.risk_level} />}>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div>
          <p className="text-xs text-slate-500">Signature Present</p>
          <p className="text-sm font-medium text-slate-900">{signature.signature_present ? "Yes" : "No"}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Image Quality</p>
          <p className="text-sm font-medium text-slate-900">{titleCase(signature.image_quality)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Similarity Score</p>
          <p className="text-sm font-medium text-slate-900">
            {signature.similarity_score === null ? "Unavailable" : formatPercent(signature.similarity_score * 100)}
          </p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Analysis Confidence</p>
          <p className="text-sm font-medium text-slate-900">{formatPercent(signature.analysis_confidence * 100)}</p>
        </div>
      </div>

      <div className="mt-3">
        <p className="text-xs text-slate-500">Status</p>
        <p className="text-sm font-medium text-slate-900">{titleCase(signature.analysis_status)}</p>
      </div>

      {signature.indicator && (
        <div className="mt-3 rounded-md bg-amber-50 p-3 text-sm text-amber-800">
          <p className="font-medium">{titleCase(signature.indicator)}</p>
          <p className="mt-1 text-amber-700">
            {INDICATOR_EXPLANATIONS[signature.indicator] || "See recommendation below for how this was handled."}
          </p>
        </div>
      )}

      <p className="mt-3 text-sm text-slate-700">
        Recommendation: <span className="font-medium">{titleCase(signature.recommendation)}</span>
      </p>
    </Card>
  );
}
