import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import App from "./App.jsx";

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              status: "healthy",
              service: "Mass Mutual Cheque Fraud Detection System",
              database: "disconnected",
            }),
        }),
      ),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders the title", () => {
    render(<App />);
    expect(
      screen.getByText("Mass Mutual Cheque Fraud Detection System"),
    ).toBeInTheDocument();
  });

  it("shows backend health information once the request resolves", async () => {
    render(<App />);
    await waitFor(() => screen.getByTestId("backend-status-ok"));
    expect(screen.getByText("healthy")).toBeInTheDocument();
  });

  it("shows an error state when the backend is unreachable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() => Promise.reject(new Error("network error"))),
    );
    render(<App />);
    await waitFor(() => screen.getByTestId("backend-status-error"));
    expect(screen.getByTestId("backend-status-error")).toHaveTextContent(
      "network error",
    );
  });
});
