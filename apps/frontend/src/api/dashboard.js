import { request } from "./client.js";

export function getDashboardSummary() {
  return request("/dashboard/summary");
}

export function getFraudStatistics() {
  return request("/dashboard/fraud-statistics");
}

export function getProcessingStatistics() {
  return request("/dashboard/processing-statistics");
}
