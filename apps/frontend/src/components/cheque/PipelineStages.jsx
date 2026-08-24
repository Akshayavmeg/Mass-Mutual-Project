import { PROCESSING_STAGES } from "../../utils/constants.js";

const STAGE_STYLES = {
  completed: "border-emerald-500 bg-emerald-500 text-white",
  in_progress: "border-amber-500 bg-amber-500 text-white",
  pending: "border-slate-300 bg-white text-slate-400",
  failed: "border-red-500 bg-red-500 text-white",
  unavailable: "border-slate-200 bg-slate-100 text-slate-400",
};

const STAGE_LABELS = {
  completed: "Completed",
  in_progress: "In progress",
  pending: "Pending",
  failed: "Failed",
  unavailable: "Unavailable",
};

/** Derives each stage's real status from the persisted cheque record --
 * never guesses/claims a stage completed unless the backend actually
 * reports it (Milestone 9's explicit requirement). Once a stage fails or
 * becomes unavailable, every later stage is marked unavailable too,
 * since the pipeline is strictly sequential. */
export function computeStageStatuses(record, runningStage) {
  const statuses = {};
  let blocked = false;

  for (const stage of PROCESSING_STAGES) {
    if (blocked) {
      statuses[stage.key] = "unavailable";
      continue;
    }
    if (stage.key === "uploaded") {
      statuses[stage.key] = "completed";
      continue;
    }
    if (runningStage === stage.key) {
      statuses[stage.key] = "in_progress";
      continue;
    }

    const value = stage.recordKey ? record?.[stage.recordKey] : null;
    if (stage.key === "preprocessed") {
      const status = value?.preprocessing_status;
      if (status === "COMPLETED") statuses[stage.key] = "completed";
      else if (status === "FAILED") {
        statuses[stage.key] = "failed";
        blocked = true;
      } else statuses[stage.key] = "pending";
      continue;
    }

    if (value) {
      const failureField = value.ocr_status ?? value.extraction_status;
      if (failureField === "FAILED") {
        statuses[stage.key] = "failed";
        blocked = true;
      } else {
        statuses[stage.key] = "completed";
      }
    } else {
      statuses[stage.key] = record?.processing_status === "FAILED" ? "unavailable" : "pending";
    }
  }
  return statuses;
}

export function PipelineStages({ record, runningStage }) {
  const statuses = computeStageStatuses(record, runningStage);
  return (
    <ol className="flex flex-wrap gap-3" data-testid="pipeline-stages">
      {PROCESSING_STAGES.map((stage, index) => {
        const status = statuses[stage.key];
        return (
          <li key={stage.key} className="flex items-center gap-2" data-testid={`stage-${stage.key}`} data-status={status}>
            <span
              className={`flex h-7 w-7 items-center justify-center rounded-full border-2 text-xs font-semibold ${STAGE_STYLES[status]}`}
              title={STAGE_LABELS[status]}
            >
              {index + 1}
            </span>
            <span className="text-xs">
              <span className="block font-medium text-slate-700">{stage.label}</span>
              <span className="text-slate-400">{STAGE_LABELS[status]}</span>
            </span>
          </li>
        );
      })}
    </ol>
  );
}
