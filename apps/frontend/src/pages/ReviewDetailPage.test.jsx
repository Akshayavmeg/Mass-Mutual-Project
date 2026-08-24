import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiError } from "../api/client.js";
import { renderWithProviders } from "../tests/testUtils.jsx";
import ReviewDetailPage from "./ReviewDetailPage.jsx";

const { getReviewCaseMock, assignReviewCaseMock, completeReviewCaseMock } = vi.hoisted(() => ({
  getReviewCaseMock: vi.fn(),
  assignReviewCaseMock: vi.fn(),
  completeReviewCaseMock: vi.fn(),
}));

vi.mock("../api/reviews.js", () => ({
  getReviewCase: getReviewCaseMock,
  assignReviewCase: assignReviewCaseMock,
  completeReviewCase: completeReviewCaseMock,
}));

const CASE = {
  review_case_id: "REV-001", cheque_id: "CHK-001", status: "QUEUED", priority: "HIGH", risk_level: "HIGH",
  trigger_reason: "Signature mismatch", triggered_rules: [],
  cheque_summary: { cheque_number: "004521", account_number_masked: "******0001", payee_name: "ABC Supplies", amount: 25000 },
  validation_results: null, fraud_results: null, signature_result: null, anomaly_results: null, risk_assessment: null,
  automated_decision: { decision: "REVIEW", decision_reason: "High risk score." },
  assigned_reviewer_id: null, comments: [], reviewer_decision: null, reviewer_comment: null,
};

describe("ReviewDetailPage", () => {
  it("requires a comment before allowing approve/reject -- never bypasses the backend's own validation rule client-side", async () => {
    getReviewCaseMock.mockResolvedValue({ ...CASE });
    renderWithProviders(<ReviewDetailPage />, { route: "/reviews/REV-001", path: "/reviews/:reviewCaseId" });

    await waitFor(() => expect(screen.getByText("REV-001", { exact: false })).toBeInTheDocument());
    fireEvent.click(screen.getByRole("button", { name: /^approve$/i }));

    expect(await screen.findByText(/comment is required/i)).toBeInTheDocument();
    expect(completeReviewCaseMock).not.toHaveBeenCalled();
  });

  it("submits a decision with a comment and reflects the backend's response", async () => {
    getReviewCaseMock.mockResolvedValueOnce({ ...CASE }).mockResolvedValueOnce({
      ...CASE, status: "CLOSED", reviewer_decision: "APPROVE", reviewer_comment: "Verified manually.",
    });
    completeReviewCaseMock.mockResolvedValue({ review_case_id: "REV-001", status: "CLOSED", final_decision: "APPROVE" });

    renderWithProviders(<ReviewDetailPage />, { route: "/reviews/REV-001", path: "/reviews/:reviewCaseId" });
    await waitFor(() => expect(screen.getByRole("button", { name: /^approve$/i })).toBeInTheDocument());

    fireEvent.change(screen.getByLabelText(/comment/i), { target: { value: "Verified manually." } });
    fireEvent.click(screen.getByRole("button", { name: /^approve$/i }));

    await waitFor(() => expect(completeReviewCaseMock).toHaveBeenCalledWith("REV-001", "APPROVE", "Verified manually."));
    expect(await screen.findByText(/this case is closed/i)).toBeInTheDocument();
  });

  it("surfaces a 403 Forbidden response instead of pretending the action succeeded", async () => {
    getReviewCaseMock.mockResolvedValue({ ...CASE });
    assignReviewCaseMock.mockRejectedValue(new ApiError("Role AUDITOR does not have permission REVIEW_UPDATE.", { status: 403 }));

    renderWithProviders(<ReviewDetailPage />, { route: "/reviews/REV-001", path: "/reviews/:reviewCaseId" });
    fireEvent.click(await screen.findByRole("button", { name: /assign to me/i }));

    await waitFor(() => expect(screen.getByText(/Forbidden/i)).toBeInTheDocument());
  });
});
