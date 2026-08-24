// Milestone 9 replaces the Milestone 0 placeholder App (which only
// rendered a health-check status card, per its own "Development
// foundation status" subtitle) with the real application shell,
// role-selection, and routing. These tests cover that real behavior;
// see the Milestone 9 report for why the M0 placeholder tests were
// replaced rather than kept alongside the real app.

import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import App from "./App.jsx";

function mockHealthyFetch() {
  vi.stubGlobal(
    "fetch",
    vi.fn((url) => {
      if (String(url).includes("/health")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ status: "healthy", service: "Mass Mutual Cheque Fraud Detection System", database: "connected" }),
        });
      }
      if (String(url).includes("/users/me")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ user_id: "DEV-OPERATOR", username: "operator_dev", role: "OPERATOR", status: "ACTIVE" }),
        });
      }
      if (String(url).includes("/dashboard/summary")) {
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              total_cheques: 0, approved: 0, under_review: 0, rejected: 0, fraud_detected: 0,
              average_processing_time_seconds: null, average_ocr_confidence: null,
            }),
        });
      }
      if (String(url).includes("/dashboard/fraud-statistics")) {
        return Promise.resolve({ ok: true, json: () => Promise.resolve({ low_risk: 0, medium_risk: 0, high_risk: 0, critical_risk: 0 }) });
      }
      if (String(url).includes("/dashboard/processing-statistics")) {
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ average_processing_time: null, ocr_success_rate: null, validation_success_rate: null, manual_review_rate: null }),
        });
      }
      return Promise.reject(new Error(`Unexpected fetch to ${url}`));
    }),
  );
}

describe("App", () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the development role-selection screen before any role is chosen", () => {
    mockHealthyFetch();
    render(<App />);
    expect(screen.getByText("Mass Mutual Cheque Fraud Detection System")).toBeInTheDocument();
    expect(screen.getByText(/Select a role to continue/i)).toBeInTheDocument();
    expect(screen.getByText(/Development Mode/i)).toBeInTheDocument();
  });

  it("navigates into the dashboard once a role is selected", async () => {
    mockHealthyFetch();
    render(<App />);
    fireEvent.click(screen.getByRole("button", { name: /continue/i }));

    await waitFor(() => expect(screen.getAllByText("Dashboard").length).toBeGreaterThan(0));
    expect(await screen.findByText("Total Cheques")).toBeInTheDocument();
  });
});
