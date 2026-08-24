import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../tests/testUtils.jsx";
import ChequeDetailPage from "./ChequeDetailPage.jsx";

const {
  getChequeMock, getAuditHistoryMock, runOcrMock, runValidationMock, runFraudAnalysisMock,
  runSignatureAnalysisMock, runAnomalyAnalysisMock, runRiskScoreMock, runDecisionMock,
} = vi.hoisted(() => ({
  getChequeMock: vi.fn(),
  getAuditHistoryMock: vi.fn(() => Promise.resolve({ cheque_id: "CHK-1", events: [] })),
  runOcrMock: vi.fn(),
  runValidationMock: vi.fn(),
  runFraudAnalysisMock: vi.fn(),
  runSignatureAnalysisMock: vi.fn(),
  runAnomalyAnalysisMock: vi.fn(),
  runRiskScoreMock: vi.fn(),
  runDecisionMock: vi.fn(),
}));

vi.mock("../api/cheques.js", () => ({
  getCheque: getChequeMock,
  getAuditHistory: getAuditHistoryMock,
  runOcr: runOcrMock,
  runValidation: runValidationMock,
  runFraudAnalysis: runFraudAnalysisMock,
  runSignatureAnalysis: runSignatureAnalysisMock,
  runAnomalyAnalysis: runAnomalyAnalysisMock,
  runRiskScore: runRiskScoreMock,
  runDecision: runDecisionMock,
}));

const BASE_RECORD = {
  cheque_id: "CHK-1", file_name: "cheque.png", file_type: "image/png", file_size: 1024,
  input_source: "UPLOAD", upload_timestamp: "2026-08-12T10:00:00Z", file_hash: "abc",
  processing_status: "UPLOADED", preprocessing: { preprocessing_status: "COMPLETED", operations: [], processing_time_ms: 5 },
  cheque_number: null, account_number: null, routing_transit_number: null, payee_name: null, amount: null, cheque_date: null,
  ocr: null, extraction: null, validation: null, fraud_analysis: null, signature_analysis: null,
  anomaly_analysis: null, risk_assessment: null, decision: null, human_decision: null,
};

const FULLY_PROCESSED_RECORD = {
  ...BASE_RECORD,
  processing_status: "UNDER_REVIEW",
  cheque_number: "004521", account_number: "9000010001", payee_name: "ABC Supplies", amount: 25000, cheque_date: "2026-08-12",
  ocr: { engine_name: "Tesseract", engine_version: "5.0", ocr_status: "COMPLETED", average_confidence: 96.5 },
  extraction: { extraction_status: "SUCCESS", template: "standard", fields: {}, missing_fields: [], ambiguous_fields: [] },
  validation: {
    overall_validation_status: "PASS", validation_message: "All checks passed.",
    checks: { ACCOUNT_EXISTS: { check: "ACCOUNT_EXISTS", status: "PASS", severity: "HIGH", message: "Account found." } },
    failed_checks: [], warnings: [], not_checked: [],
  },
  fraud_analysis: {
    fraud_risk_score: 18.5, risk_level: "LOW", tampering_detected: false, model_prediction: "LOW_RISK",
    indicators: [], rule_violations: [], explanation: [], unavailable_inputs: [],
    duplicate_analysis: { duplicate_status: "NEW" }, image_analysis: { image_tampering_score: 0.1 },
  },
  signature_analysis: {
    signature_present: true, image_quality: "GOOD", similarity_score: 0.91, analysis_confidence: 0.95,
    risk_level: "LOW", indicator: null, recommendation: "APPROVE", analysis_status: "COMPLETED",
  },
  anomaly_analysis: { anomaly_score: 12.5, risk_level: "LOW", anomalies: [], model_name: "anomaly-v1", analysis_status: "COMPLETED", unavailable_inputs: [] },
  risk_assessment: { overall_risk_score: 61.5, risk_level: "HIGH", risk_factors: [], hard_rules_triggered: [], unavailable_inputs: [], config_version: "risk-v1.0" },
  decision: {
    decision: "REVIEW", decision_reason: "High fraud score and signature mismatch detected.", reasons: [],
    triggered_rules: [], risk_score: 61.5, risk_level: "HIGH", requires_manual_review: true,
    escalation_reason: null, unavailable_inputs: [], ruleset_version: "v1", policy_version: "v1",
    decision_timestamp: "2026-08-12T10:00:15Z", evidence: {},
  },
};

describe("ChequeDetailPage", () => {
  it("shows pending stages and a working 'run next stage' action for a freshly-uploaded cheque", async () => {
    getChequeMock.mockResolvedValue({ ...BASE_RECORD });
    runOcrMock.mockResolvedValue({ cheque_id: "CHK-1", status: "COMPLETED", ocr_confidence: 96 });

    renderWithProviders(<ChequeDetailPage />, { route: "/cheques/CHK-1", path: "/cheques/:chequeId" });

    await waitFor(() => expect(screen.getByTestId("stage-ocr")).toHaveAttribute("data-status", "pending"));
    expect(screen.getByTestId("stage-uploaded")).toHaveAttribute("data-status", "completed");

    fireEvent.click(screen.getByRole("button", { name: /run next stage/i }));
    await waitFor(() => expect(runOcrMock).toHaveBeenCalledWith("CHK-1"));
  });

  it("never claims a stage completed unless the backend actually reports it -- does not fabricate decision results", async () => {
    getChequeMock.mockResolvedValue({ ...BASE_RECORD, ocr: FULLY_PROCESSED_RECORD.ocr });

    renderWithProviders(<ChequeDetailPage />, { route: "/cheques/CHK-1", path: "/cheques/:chequeId" });

    await waitFor(() => expect(screen.getByTestId("stage-ocr")).toHaveAttribute("data-status", "completed"));
    expect(screen.getByTestId("stage-decision")).toHaveAttribute("data-status", "pending");
    expect(screen.queryByText("APPROVE")).not.toBeInTheDocument();
    expect(screen.queryByText("REJECT")).not.toBeInTheDocument();
  });

  it("renders every result section for a fully processed cheque, sourced only from the API response", async () => {
    getChequeMock.mockResolvedValue(FULLY_PROCESSED_RECORD);

    renderWithProviders(<ChequeDetailPage />, { route: "/cheques/CHK-1", path: "/cheques/:chequeId" });

    await waitFor(() => expect(screen.getByTestId("stage-decision")).toHaveAttribute("data-status", "completed"));
    expect(screen.getByText("High fraud score and signature mismatch detected.")).toBeInTheDocument();
    expect(screen.getByText("ABC Supplies")).toBeInTheDocument();
  });
});
