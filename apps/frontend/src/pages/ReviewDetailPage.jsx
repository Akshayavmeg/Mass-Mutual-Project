import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { assignReviewCase, completeReviewCase, getReviewCase } from "../api/reviews.js";
import { AnomalyPanel } from "../components/cheque/AnomalyPanel.jsx";
import { ChequeImages } from "../components/cheque/ChequeImages.jsx";
import { FraudPanel } from "../components/cheque/FraudPanel.jsx";
import { RiskPanel } from "../components/cheque/RiskPanel.jsx";
import { SignaturePanel } from "../components/cheque/SignaturePanel.jsx";
import { ValidationPanel } from "../components/cheque/ValidationPanel.jsx";
import { DecisionBadge, RiskBadge, SeverityBadge, StatusBadge } from "../components/common/Badge.jsx";
import { Card } from "../components/common/Card.jsx";
import { EmptyState, ErrorState, LoadingState } from "../components/common/States.jsx";
import { useApi } from "../hooks/useApi.js";
import { useUser } from "../context/UserContext.jsx";
import { useNotifications } from "../layouts/NotificationContext.jsx";
import { formatCurrency, formatDate } from "../utils/format.js";

const TERMINAL_STATUSES = ["CLOSED"];

export default function ReviewDetailPage() {
  const { reviewCaseId } = useParams();
  const { userId } = useUser();
  const { notify } = useNotifications();
  const navigate = useNavigate();
  const [comment, setComment] = useState("");
  const [busy, setBusy] = useState(false);
  const [actionError, setActionError] = useState(null);

  const { data: reviewCase, error, loading, refetch } = useApi(() => getReviewCase(reviewCaseId), [reviewCaseId]);

  async function handleAssign() {
    setBusy(true);
    setActionError(null);
    try {
      await assignReviewCase(reviewCaseId, userId || "USR-DEV");
      notify("Case assigned to you.", "success");
      await refetch();
    } catch (err) {
      setActionError(err);
      notify(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  async function handleComplete(decision) {
    if (!comment.trim()) {
      setActionError({ message: "A comment is required to complete a review." });
      return;
    }
    setBusy(true);
    setActionError(null);
    try {
      await completeReviewCase(reviewCaseId, decision, comment.trim());
      notify(`Review case ${decision === "APPROVE" ? "approved" : "rejected"}.`, "success");
      await refetch();
    } catch (err) {
      setActionError(err);
      notify(err.message, "error");
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <LoadingState label="Loading review case…" />;
  if (error) return <ErrorState error={error} onRetry={refetch} />;
  if (!reviewCase) {
    return <EmptyState title="Review case not found" message={`No review case with ID ${reviewCaseId} exists.`} />;
  }

  const isClosed = TERMINAL_STATUSES.includes(reviewCase.status);
  const summary = reviewCase.cheque_summary ?? {};

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Review Case {reviewCase.review_case_id}</h1>
          <p className="text-sm text-slate-500">
            Cheque{" "}
            <button
              type="button"
              onClick={() => navigate(`/cheques/${reviewCase.cheque_id}`)}
              className="font-mono text-xs text-slate-700 underline"
            >
              {reviewCase.cheque_id}
            </button>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <SeverityBadge severity={reviewCase.priority} />
          <RiskBadge level={reviewCase.risk_level} />
          <StatusBadge status={reviewCase.status} />
        </div>
      </div>

      <Card title="Trigger">
        <p className="text-sm text-slate-700">{reviewCase.trigger_reason}</p>
        {reviewCase.triggered_rules?.length > 0 && (
          <p className="mt-1 text-xs text-slate-500">Rules: {reviewCase.triggered_rules.join(", ")}</p>
        )}
      </Card>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div>
          <p className="text-xs text-slate-500">Cheque Number</p>
          <p className="text-sm font-medium text-slate-900">{summary.cheque_number ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Account</p>
          <p className="text-sm font-medium text-slate-900">{summary.account_number_masked ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Payee</p>
          <p className="text-sm font-medium text-slate-900">{summary.payee_name ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Amount</p>
          <p className="text-sm font-medium text-slate-900">{formatCurrency(summary.amount)}</p>
        </div>
      </div>

      <ChequeImages chequeId={reviewCase.cheque_id} />

      <Card title="Automated Decision">
        <div className="flex items-center gap-3">
          <DecisionBadge decision={reviewCase.automated_decision?.decision} />
          <p className="text-sm text-slate-700">{reviewCase.automated_decision?.decision_reason}</p>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ValidationPanel validation={reviewCase.validation_results} />
        <FraudPanel fraud={reviewCase.fraud_results} />
        <SignaturePanel signature={reviewCase.signature_result} />
        <AnomalyPanel anomaly={reviewCase.anomaly_results} />
        <RiskPanel risk={reviewCase.risk_assessment} />
      </div>

      <Card title="Review History">
        {reviewCase.comments?.length > 0 ? (
          <ul className="space-y-2 text-sm">
            {reviewCase.comments.map((c, i) => (
              <li key={i} className="rounded-md border border-slate-200 p-2">
                <p className="text-xs font-medium text-slate-700">
                  {c.author} · {formatDate(c.timestamp)}
                </p>
                <p className="mt-1 text-slate-600">{c.comment}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-slate-500">No comments yet.</p>
        )}
      </Card>

      <Card title="Reviewer Actions">
        {isClosed ? (
          <div>
            <p className="text-sm text-slate-700">
              This case is closed. Final decision: <DecisionBadge decision={reviewCase.reviewer_decision} />
            </p>
            <p className="mt-1 text-sm text-slate-600">{reviewCase.reviewer_comment}</p>
          </div>
        ) : (
          <div className="space-y-3">
            {!reviewCase.assigned_reviewer_id && (
              <button
                type="button"
                onClick={handleAssign}
                disabled={busy}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
              >
                Assign to me
              </button>
            )}
            <div>
              <label htmlFor="review-comment" className="block text-sm font-medium text-slate-700">
                Comment <span className="text-slate-400">(required to approve or reject)</span>
              </label>
              <textarea
                id="review-comment"
                rows={3}
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                className="mt-1 block w-full rounded-md border border-slate-300 px-3 py-2 text-sm focus:border-slate-500 focus:outline-none"
                placeholder="Document your reasoning for this decision…"
              />
            </div>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => handleComplete("APPROVE")}
                disabled={busy}
                className="rounded-md bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-700 disabled:opacity-40"
              >
                Approve
              </button>
              <button
                type="button"
                onClick={() => handleComplete("REJECT")}
                disabled={busy}
                className="rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-40"
              >
                Reject
              </button>
            </div>
            {actionError && <ErrorState error={actionError} />}
          </div>
        )}
      </Card>
    </div>
  );
}
