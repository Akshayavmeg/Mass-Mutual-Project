import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, NetworkError, request, setRequestUserContext } from "./client.js";

describe("request()", () => {
  beforeEach(() => {
    setRequestUserContext({ role: null, userId: null });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
    setRequestUserContext({ role: null, userId: null });
  });

  it("attaches the dev-mode role/user headers once set", async () => {
    setRequestUserContext({ role: "REVIEWER", userId: "USR-002" });
    const fetchMock = vi.fn(() => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({ ok: true }) }));
    vi.stubGlobal("fetch", fetchMock);

    await request("/reviews");

    const [, init] = fetchMock.mock.calls[0];
    expect(init.headers["X-User-Role"]).toBe("REVIEWER");
    expect(init.headers["X-User-Id"]).toBe("USR-002");
  });

  it("parses the documented {error:{code,message,request_id}} envelope into an ApiError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(() =>
        Promise.resolve({
          ok: false,
          status: 404,
          json: () =>
            Promise.resolve({ error: { code: "CHEQUE_NOT_FOUND", message: "The requested cheque does not exist.", request_id: "REQ-1" } }),
        }),
      ),
    );

    await expect(request("/cheques/CHK-DOES-NOT-EXIST")).rejects.toMatchObject({
      name: "ApiError", status: 404, code: "CHEQUE_NOT_FOUND", requestId: "REQ-1",
    });
  });

  it("raises a NetworkError (not a silent success) when fetch itself fails", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.reject(new TypeError("Failed to fetch"))));
    await expect(request("/health")).rejects.toBeInstanceOf(NetworkError);
  });

  it("drops empty query parameters instead of sending them as literal empty strings", async () => {
    const fetchMock = vi.fn(() => Promise.resolve({ ok: true, status: 200, json: () => Promise.resolve({}) }));
    vi.stubGlobal("fetch", fetchMock);

    await request("/cheques", { query: { status: "", risk_level: "HIGH" } });

    const [url] = fetchMock.mock.calls[0];
    expect(url).toContain("risk_level=HIGH");
    expect(url).not.toContain("status=");
  });
});

describe("ApiError", () => {
  it("carries status/code/requestId for callers to branch on", () => {
    const err = new ApiError("nope", { status: 403, code: "FORBIDDEN", requestId: "REQ-9" });
    expect(err.status).toBe(403);
    expect(err.code).toBe("FORBIDDEN");
    expect(err.requestId).toBe("REQ-9");
  });
});
