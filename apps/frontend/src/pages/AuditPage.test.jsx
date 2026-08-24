import { fireEvent, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { renderWithProviders } from "../tests/testUtils.jsx";
import AuditPage from "./AuditPage.jsx";

const { getAuditHistoryMock } = vi.hoisted(() => ({ getAuditHistoryMock: vi.fn() }));
vi.mock("../api/cheques.js", () => ({ getAuditHistory: getAuditHistoryMock }));

describe("AuditPage", () => {
  it("prompts for a Cheque ID when none is selected", () => {
    renderWithProviders(<AuditPage />, { route: "/audit", path: "/audit" });
    expect(screen.getByText(/no cheque selected/i)).toBeInTheDocument();
  });

  it("renders the append-only audit trail for a looked-up cheque", async () => {
    getAuditHistoryMock.mockResolvedValue({
      cheque_id: "CHK-1",
      events: [
        {
          audit_id: "AUD-1", cheque_id: "CHK-1", event_type: "CHEQUE_UPLOADED", event_timestamp: "2026-08-12T10:00:00Z",
          user_id: null, user_role: null, source: "USER", previous_status: null, new_status: "UPLOADED",
          action: "UPLOAD", result: "SUCCESS", reason: null, request_id: "REQ-1", metadata: null,
        },
      ],
    });

    renderWithProviders(<AuditPage />, { route: "/audit/CHK-1", path: "/audit/:chequeId" });

    await waitFor(() => expect(screen.getByText("Cheque Uploaded")).toBeInTheDocument());
    expect(screen.getAllByText(/append-only/i).length).toBeGreaterThan(0);
    expect(screen.queryByRole("button", { name: /delete/i })).not.toBeInTheDocument();
  });
});
