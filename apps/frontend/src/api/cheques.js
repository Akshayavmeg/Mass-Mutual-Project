import { request } from "./client.js";

export function uploadCheque(file) {
  const formData = new FormData();
  formData.append("file", file);
  return request("/cheques/upload", { method: "POST", formData });
}

export function listCheques({ page = 1, limit = 20, status, riskLevel } = {}) {
  return request("/cheques", { query: { page, limit, status, risk_level: riskLevel } });
}

export function getCheque(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}`);
}

export function runOcr(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/ocr`, { method: "POST" });
}

export function getOcrResult(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/ocr`);
}

export function runValidation(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/validate`, { method: "POST" });
}

export function getValidationResult(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/validation`);
}

export function runFraudAnalysis(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/fraud-analysis`, { method: "POST" });
}

export function getFraudAnalysis(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/fraud-analysis`);
}

export function runSignatureAnalysis(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/signature-analysis`, { method: "POST" });
}

export function runAnomalyAnalysis(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/anomaly-analysis`, { method: "POST" });
}

export function runRiskScore(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/risk-score`, { method: "POST" });
}

export function runDecision(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/decision`, { method: "POST" });
}

export function getDecision(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/decision`);
}

export function getAuditHistory(chequeId) {
  return request(`/cheques/${encodeURIComponent(chequeId)}/audit`);
}

/** Runs the full processing pipeline for a cheque sequentially, calling
 * `onStageComplete(stageName, result)` after each stage so the caller
 * can render live progress. Stops (without throwing further) if a stage
 * fails, since later stages depend on earlier ones having succeeded. */
export async function runFullPipeline(chequeId, onStageComplete) {
  const stages = [
    ["ocr", runOcr],
    ["validation", runValidation],
    ["fraud_analysis", runFraudAnalysis],
    ["signature_analysis", runSignatureAnalysis],
    ["anomaly_analysis", runAnomalyAnalysis],
    ["risk_assessment", runRiskScore],
    ["decision", runDecision],
  ];
  for (const [name, run] of stages) {
    const result = await run(chequeId);
    onStageComplete?.(name, result);
  }
}
