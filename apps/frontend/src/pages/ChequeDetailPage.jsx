import { useCallback, useState } from "react";
import { useParams } from "react-router-dom";
import {
  getAuditHistory, getCheque, runAnomalyAnalysis, runDecision, runFraudAnalysis,
  runOcr, runRiskScore, runSignatureAnalysis, runValidation,
} from "../api/cheques.js";
import { AnomalyPanel } from "../components/cheque/AnomalyPanel.jsx";
import { AuditTimeline } from "../components/cheque/AuditTimeline.jsx";
import { ChequeImages } from "../components/cheque/ChequeImages.jsx";
import { DecisionPanel } from "../components/cheque/DecisionPanel.jsx";
import { ExtractedFieldsPanel } from "../components/cheque/ExtractedFieldsPanel.jsx";
import { FraudPanel } from "../components/cheque/FraudPanel.jsx";
import { computeStageStatuses, PipelineStages } from "../components/cheque/PipelineStages.jsx";
import { RiskPanel } from "../components/cheque/RiskPanel.jsx";
import { SignaturePanel } from "../components/cheque/SignaturePanel.jsx";
import { ValidationPanel } from "../components/cheque/ValidationPanel.jsx";
import { Badge, StatusBadge } from "../components/common/Badge.jsx";
import { Card } from "../components/common/Card.jsx";
import { ErrorState, LoadingState } from "../components/common/States.jsx";
import { useApi } from "../hooks/useApi.js";
import { useNotifications } from "../layouts/NotificationContext.jsx";
import { formatCurrency, formatDateOnly, maskAccountNumber } from "../utils/format.js";

const STAGE_RUNNERS = [
  ["ocr", "OCR", runOcr],
  ["validation", "Validation", runValidation],
  ["fraud_analysis", "Fraud Analysis", runFraudAnalysis],
  ["signature_analysis", "Signature Analysis", runSignatureAnalysis],
  ["anomaly_analysis", "Anomaly Analysis", runAnomalyAnalysis],
  ["risk_assessment", "Risk Scoring", runRiskScore],
  ["decision", "Decision", runDecision],
];

const TABS = ["Overview", "Extraction", "Validation", "Fraud", "Signature", "Anomaly", "Risk", "Decision", "Audit"];

export default function ChequeDetailPage() {
  const { chequeId } = useParams();
  const { notify } = useNotifications();
  const [tab, setTab] = useState("Overview");
  const [runningStage, setRunningStage] = useState(null);
  const [runError, setRunError] = useState(null);

  const fetchAll = useCallback(async () => {
    const [record, audit] = await Promise.all([
      getCheque(chequeId),
      getAuditHistory(chequeId).catch(() => ({ events: [] })),
    ]);
    return { record, audit: audit.events };
  }, [chequeId]);

  const { data, error, loading, refetch } = useApi(fetchAll, [chequeId]);

  async function runNextStage() {
    if (!data) return;
    const statuses = computeStageStatuses(data.record, null);
    const next = STAGE_RUNNERS.find(([key]) => statuses[key] === "pending");
    if (!next) return;
    const [key, label, run] = next;
    setRunningStage(key);
    setRunError(null);
    try {
      await run(chequeId);
      notify(`${label} completed.`, "success");
      await refetch();
    } catch (err) {
      setRunError(err);
      notify(`${label} failed: ${err.message}`, "error");
    } finally {
      setRunningStage(null);
    }
  }

  async function runAllRemaining() {
    if (!data) return;
    let statuses = computeStageStatuses(data.record, null);
    let record = data.record;
    for (const [key, label, run] of STAGE_RUNNERS) {
      statuses = computeStageStatuses(record, null);
      if (statuses[key] !== "pending") continue;
      setRunningStage(key);
      setRunError(null);
      try {
        await run(chequeId);
        record = await getCheque(chequeId);
      } catch (err) {
        setRunError(err);
        notify(`${label} failed: ${err.message}`, "error");
        setRunningStage(null);
        await refetch();
        return;
      }
    }
    setRunningStage(null);
    notify("Processing pipeline complete.", "success");
    await refetch();
  }

  if (loading) return <LoadingState label="Loading cheque…" />;
  if (error) return <ErrorState error={error} onRetry={refetch} />;

  const { record, audit } = data;
  const statuses = computeStageStatuses(record, runningStage);
  const hasPending = Object.values(statuses).some((s) => s === "pending");

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-slate-900">Cheque {record.cheque_id}</h1>
          <p className="text-sm text-slate-500">
            Uploaded {formatDateOnly(record.upload_timestamp)} · {record.file_name}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <StatusBadge status={record.processing_status} />
          {record.decision && <Badge className="bg-slate-900 text-white">{record.decision.decision}</Badge>}
        </div>
      </div>

      <Card title="Processing Pipeline">
        <PipelineStages record={record} runningStage={runningStage} />
        <div className="mt-4 flex flex-wrap gap-2">
          <button
            type="button"
            onClick={runNextStage}
            disabled={!hasPending || runningStage !== null}
            className="rounded-md bg-slate-900 px-3 py-1.5 text-sm font-medium text-white hover:bg-slate-800 disabled:opacity-40"
          >
            {runningStage ? "Running…" : "Run next stage"}
          </button>
          <button
            type="button"
            onClick={runAllRemaining}
            disabled={!hasPending || runningStage !== null}
            className="rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50 disabled:opacity-40"
          >
            Run all remaining stages
          </button>
        </div>
        {runError && <div className="mt-3"><ErrorState error={runError} /></div>}
      </Card>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <div>
          <p className="text-xs text-slate-500">Cheque Number</p>
          <p className="text-sm font-medium text-slate-900">{record.cheque_number ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Account Number</p>
          <p className="text-sm font-medium text-slate-900">{maskAccountNumber(record.account_number)}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Payee</p>
          <p className="text-sm font-medium text-slate-900">{record.payee_name ?? "—"}</p>
        </div>
        <div>
          <p className="text-xs text-slate-500">Amount</p>
          <p className="text-sm font-medium text-slate-900">{formatCurrency(record.amount)}</p>
        </div>
      </div>

      <ChequeImages chequeId={chequeId} />

      <nav className="flex flex-wrap gap-1 border-b border-slate-200">
        {TABS.map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            className={`rounded-t-md px-3 py-2 text-sm font-medium ${
              tab === t ? "border-b-2 border-slate-900 text-slate-900" : "text-slate-500 hover:text-slate-700"
            }`}
          >
            {t}
          </button>
        ))}
      </nav>

      <div>
        {tab === "Overview" && (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <ValidationPanel validation={record.validation} />
            <FraudPanel fraud={record.fraud_analysis} />
            <SignaturePanel signature={record.signature_analysis} />
            <AnomalyPanel anomaly={record.anomaly_analysis} />
            <RiskPanel risk={record.risk_assessment} />
            <DecisionPanel decision={record.decision} humanDecision={record.human_decision} />
          </div>
        )}
        {tab === "Extraction" && <ExtractedFieldsPanel ocr={record.ocr} extraction={record.extraction} />}
        {tab === "Validation" && <ValidationPanel validation={record.validation} />}
        {tab === "Fraud" && <FraudPanel fraud={record.fraud_analysis} />}
        {tab === "Signature" && <SignaturePanel signature={record.signature_analysis} />}
        {tab === "Anomaly" && <AnomalyPanel anomaly={record.anomaly_analysis} />}
        {tab === "Risk" && <RiskPanel risk={record.risk_assessment} />}
        {tab === "Decision" && <DecisionPanel decision={record.decision} humanDecision={record.human_decision} />}
        {tab === "Audit" && (
          <Card title="Audit History">
            <AuditTimeline events={audit} />
          </Card>
        )}
      </div>
    </div>
  );
}
