import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../tests/testUtils.jsx";
import DashboardPage from "./DashboardPage.jsx";

vi.mock("../api/dashboard.js", () => ({
  getDashboardSummary: vi.fn(() =>
    Promise.resolve({
      total_cheques: 42, approved: 30, under_review: 8, rejected: 4, fraud_detected: 5,
      average_processing_time_seconds: 12.3, average_ocr_confidence: 96.5,
    }),
  ),
  getFraudStatistics: vi.fn(() => Promise.resolve({ low_risk: 30, medium_risk: 8, high_risk: 3, critical_risk: 1 })),
  getProcessingStatistics: vi.fn(() =>
    Promise.resolve({ average_processing_time: 12.3, ocr_success_rate: 97.1, validation_success_rate: 94.8, manual_review_rate: 19.0 }),
  ),
}));

describe("DashboardPage", () => {
  it("renders real backend-derived metrics, not fabricated values", async () => {
    renderWithProviders(<DashboardPage />);
    await waitFor(() => expect(screen.getByText("42")).toBeInTheDocument());
    expect(screen.getAllByText("30").length).toBeGreaterThan(0); // approved (StatCard + bar chart)
    expect(screen.getByText("97.1%")).toBeInTheDocument(); // ocr success rate
  });
});
