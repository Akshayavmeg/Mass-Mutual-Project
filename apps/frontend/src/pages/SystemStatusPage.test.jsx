import { screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { NetworkError } from "../api/client.js";
import { renderWithProviders } from "../tests/testUtils.jsx";
import SystemStatusPage from "./SystemStatusPage.jsx";

const { getHealthMock } = vi.hoisted(() => ({ getHealthMock: vi.fn() }));
vi.mock("../api/client.js", async (importOriginal) => {
  const actual = await importOriginal();
  return { ...actual, getHealth: getHealthMock };
});

describe("SystemStatusPage", () => {
  it("shows a healthy, connected status", async () => {
    getHealthMock.mockResolvedValue({ status: "healthy", service: "cheque-processing-api", database: "connected" });
    renderWithProviders(<SystemStatusPage />, { route: "/status" });
    await waitFor(() => expect(screen.getByText("healthy")).toBeInTheDocument());
    expect(screen.getByText("connected")).toBeInTheDocument();
  });

  it("clearly shows a degraded database state rather than hiding it", async () => {
    getHealthMock.mockResolvedValue({ status: "unhealthy", service: "cheque-processing-api", database: "disconnected" });
    renderWithProviders(<SystemStatusPage />, { route: "/status" });
    await waitFor(() => expect(screen.getByText("disconnected")).toBeInTheDocument());
    expect(screen.getByText(/fallback repositories/i)).toBeInTheDocument();
  });

  it("shows an unreachable state when the backend cannot be reached at all", async () => {
    getHealthMock.mockRejectedValue(new NetworkError("fetch failed"));
    renderWithProviders(<SystemStatusPage />, { route: "/status" });
    await waitFor(() => expect(screen.getByText(/backend unreachable/i)).toBeInTheDocument());
  });
});
