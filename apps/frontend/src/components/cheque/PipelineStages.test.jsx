import { describe, expect, it } from "vitest";
import { computeStageStatuses } from "./PipelineStages.jsx";

describe("computeStageStatuses", () => {
  it("marks only 'uploaded' as completed for a brand-new record", () => {
    const statuses = computeStageStatuses({ processing_status: "UPLOADED" }, null);
    expect(statuses.uploaded).toBe("completed");
    expect(statuses.ocr).toBe("pending");
    expect(statuses.decision).toBe("pending");
  });

  it("marks a stage in_progress while it is actively running", () => {
    const statuses = computeStageStatuses({ processing_status: "UPLOADED" }, "ocr");
    expect(statuses.ocr).toBe("in_progress");
    expect(statuses.validation).toBe("pending");
  });

  it("marks a stage failed and every later stage unavailable, never fabricating downstream completion", () => {
    const record = { processing_status: "FAILED", ocr: { ocr_status: "FAILED" } };
    const statuses = computeStageStatuses(record, null);
    expect(statuses.ocr).toBe("failed");
    expect(statuses.extraction).toBe("unavailable");
    expect(statuses.validation).toBe("unavailable");
    expect(statuses.decision).toBe("unavailable");
  });

  it("marks preprocessing failure as blocking every later stage", () => {
    const record = { preprocessing: { preprocessing_status: "FAILED" } };
    const statuses = computeStageStatuses(record, null);
    expect(statuses.preprocessed).toBe("failed");
    expect(statuses.ocr).toBe("unavailable");
  });

  it("marks a completed stage as completed only when the backend actually persisted a result", () => {
    const record = {
      processing_status: "OCR_COMPLETED",
      preprocessing: { preprocessing_status: "COMPLETED" },
      ocr: { ocr_status: "COMPLETED" },
    };
    const statuses = computeStageStatuses(record, null);
    expect(statuses.ocr).toBe("completed");
    expect(statuses.validation).toBe("pending");
  });
});
