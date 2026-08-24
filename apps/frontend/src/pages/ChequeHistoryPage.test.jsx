import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../tests/testUtils.jsx";
import ChequeHistoryPage from "./ChequeHistoryPage.jsx";

const { listChequesMock } = vi.hoisted(() => ({ listChequesMock: vi.fn() }));
vi.mock("../api/cheques.js", () => ({ listCheques: listChequesMock }));

describe("ChequeHistoryPage", () => {
  it("renders persisted cheque records from the backend, not fabricated rows", async () => {
    listChequesMock.mockResolvedValue({
      page: 1, limit: 20, total: 2,
      cheques: [
        { cheque_id: "CHK-1", amount: 1000, risk_level: "LOW", status: "APPROVED", payee_name: "Alice", upload_timestamp: "2026-08-01T00:00:00Z", decision: "APPROVE" },
        { cheque_id: "CHK-2", amount: 5000, risk_level: "HIGH", status: "UNDER_REVIEW", payee_name: "Bob", upload_timestamp: "2026-08-02T00:00:00Z", decision: null },
      ],
    });

    renderWithProviders(<ChequeHistoryPage />, { route: "/cheques" });

    await waitFor(() => expect(screen.getByText("CHK-1")).toBeInTheDocument());
    expect(screen.getByText("CHK-2")).toBeInTheDocument();
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(listChequesMock).toHaveBeenCalledWith({ page: 1, limit: 20, status: "", riskLevel: "" });
  });

  it("shows an empty state when there are no matching cheques", async () => {
    listChequesMock.mockResolvedValue({ page: 1, limit: 20, total: 0, cheques: [] });
    renderWithProviders(<ChequeHistoryPage />, { route: "/cheques" });
    await waitFor(() => expect(screen.getByTestId("empty-state")).toBeInTheDocument());
  });
});
