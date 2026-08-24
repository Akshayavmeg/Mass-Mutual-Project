import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../tests/testUtils.jsx";
import ReviewQueuePage from "./ReviewQueuePage.jsx";

const { getReviewQueueMock } = vi.hoisted(() => ({ getReviewQueueMock: vi.fn() }));
vi.mock("../api/reviews.js", () => ({ getReviewQueue: getReviewQueueMock }));

describe("ReviewQueuePage", () => {
  it("renders review cases returned by the backend", async () => {
    getReviewQueueMock.mockResolvedValue({
      total: 1,
      cases: [
        {
          review_case_id: "REV-001", cheque_id: "CHK-001", status: "QUEUED", priority: "HIGH",
          trigger_reason: "Signature mismatch", risk_level: "HIGH",
          cheque_summary: { amount: 25000 }, assigned_reviewer_id: null, created_at: "2026-08-12T10:00:00Z",
        },
      ],
    });

    renderWithProviders(<ReviewQueuePage />, { route: "/reviews" });

    await waitFor(() => expect(screen.getByText("REV-001")).toBeInTheDocument());
    expect(screen.getByText("CHK-001")).toBeInTheDocument();
    expect(screen.getByText("Unassigned")).toBeInTheDocument();
  });

  it("shows an empty state when the queue has no matching cases", async () => {
    getReviewQueueMock.mockResolvedValue({ total: 0, cases: [] });
    renderWithProviders(<ReviewQueuePage />, { route: "/reviews" });
    await waitFor(() => expect(screen.getByTestId("empty-state")).toBeInTheDocument());
  });
});
