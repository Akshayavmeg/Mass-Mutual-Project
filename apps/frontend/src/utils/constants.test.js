import { describe, expect, it } from "vitest";
import { PERMISSION, roleHasPermission } from "./constants.js";

describe("roleHasPermission", () => {
  it("mirrors the backend's REVIEWER permissions", () => {
    expect(roleHasPermission("REVIEWER", PERMISSION.REVIEW_UPDATE)).toBe(true);
    expect(roleHasPermission("REVIEWER", PERMISSION.CHEQUE_UPLOAD)).toBe(false);
  });

  it("mirrors the backend's AUDITOR permissions (read-only)", () => {
    expect(roleHasPermission("AUDITOR", PERMISSION.AUDIT_VIEW)).toBe(true);
    expect(roleHasPermission("AUDITOR", PERMISSION.REVIEW_UPDATE)).toBe(false);
  });

  it("returns false for an unrecognized or missing role", () => {
    expect(roleHasPermission(null, PERMISSION.CHEQUE_VIEW)).toBe(false);
    expect(roleHasPermission("NOT_A_ROLE", PERMISSION.CHEQUE_VIEW)).toBe(false);
  });
});
