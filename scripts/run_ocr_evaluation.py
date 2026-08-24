"""OCR evaluation (docs/32_OCR_Evaluation.md).

Runs the real upload -> preprocess -> OCR -> extraction pipeline (the
same code path the API uses) against every cheque in the Milestone 1
ground-truth dataset and measures actual field-level and overall OCR
extraction accuracy.

This script produces MEASURED results only. Per docs/32 S20 ("We should
not claim 95% or higher until the system has actually been tested"), it
never enters a fabricated number -- every value in the output files and
summary comes from actually running the pipeline and comparing against
the Milestone 1 ground truth.

Ground truth here is what is actually PRINTED on the cheque image
(docs/25's `cheques` fields), not the bank's expected_* record -- OCR has
no way to know the "true" bank record, only what the pixels say. Cheques
in tampered categories (PAYEE_TAMPERED/AMOUNT_TAMPERED) are therefore
evaluated against the tampered value that is genuinely printed on their
image, which is the only thing OCR could possibly read correctly.

Run with the backend virtual environment:
    apps/backend/.venv/Scripts/python.exe scripts/run_ocr_evaluation.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parents[1] / "apps" / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.repositories.cheque_repository import get_cheque_repository  # noqa: E402
from app.services.cheque import input_service  # noqa: E402
from app.services.ocr import pipeline as ocr_pipeline  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
GROUND_TRUTH_PATH = DATA_DIR / "test_data" / "cheques_ground_truth.csv"
TEST_DATA_DIR = DATA_DIR / "test_data"

# The canonical field set evaluated, per docs/32_OCR_Evaluation.md S4
# (cheque number, account number, routing/transit number, payee, amount,
# date), using this project's standardized field names (ADR-0007 /
# Milestone 0 consistency work: payee_name, routing_transit_number).
EVALUATED_FIELDS = [
    "cheque_number", "account_number", "routing_transit_number", "payee_name", "amount", "date",
]

# Ground-truth CSV column -> extracted-field name (they differ only for date).
GROUND_TRUTH_COLUMN = {
    "cheque_number": "cheque_number",
    "account_number": "account_number",
    "routing_transit_number": "routing_transit_number",
    "payee_name": "payee_name",
    "amount": "amount",
    "date": "cheque_date",
}


def _values_match(field: str, predicted, expected) -> bool:
    if predicted is None:
        return False
    if field == "amount":
        try:
            return abs(float(predicted) - float(expected)) < 0.01
        except (TypeError, ValueError):
            return False
    if field == "cheque_number":
        # Ground truth CSV may load as int (losing leading zeros); compare
        # zero-padded to 6 digits, matching this project's cheque number format.
        return str(predicted).zfill(6) == str(expected).zfill(6)
    return str(predicted).strip() == str(expected).strip()


def run_evaluation() -> dict:
    df = pd.read_csv(GROUND_TRUTH_PATH, dtype={
        "account_number": str, "cheque_number": str, "routing_transit_number": str,
    })

    repo = get_cheque_repository()
    predictions_rows = []
    field_correct = {f: 0 for f in EVALUATED_FIELDS}
    field_total = {f: 0 for f in EVALUATED_FIELDS}
    ocr_processing_times = []
    extraction_processing_times = []
    ocr_status_counts: dict[str, int] = {}
    extraction_status_counts: dict[str, int] = {}

    start = time.perf_counter()

    for _, row in df.iterrows():
        image_path = DATA_DIR / row["image_path"]
        content = image_path.read_bytes()

        upload_record = input_service.handle_upload(image_path.name, content)
        cheque_id = upload_record["cheque_id"]

        try:
            result = ocr_pipeline.run_ocr_and_extraction(cheque_id)
        except Exception as exc:  # noqa: BLE001 - a single bad sample must not abort the whole evaluation
            predictions_rows.append({
                "cheque_id": row["cheque_id"], "category": row["category"],
                "ocr_status": "ERROR", "extraction_status": "ERROR", "error": str(exc),
            })
            continue

        ocr = result["ocr"]
        extraction = result["extraction"]
        ocr_status_counts[ocr["ocr_status"]] = ocr_status_counts.get(ocr["ocr_status"], 0) + 1
        extraction_status_counts[extraction["extraction_status"]] = (
            extraction_status_counts.get(extraction["extraction_status"], 0) + 1
        )
        ocr_processing_times.append(ocr["processing_time_ms"])
        extraction_processing_times.append(extraction["processing_time_ms"])

        pred_row = {
            "cheque_id": row["cheque_id"], "category": row["category"],
            "ocr_status": ocr["ocr_status"], "ocr_confidence": ocr["average_confidence"],
            "extraction_status": extraction["extraction_status"],
        }

        for field in EVALUATED_FIELDS:
            gt_column = GROUND_TRUTH_COLUMN[field]
            expected = row[gt_column]
            predicted = extraction["fields"].get(field, {}).get("value")
            correct = _values_match(field, predicted, expected)

            field_total[field] += 1
            if correct:
                field_correct[field] += 1

            pred_row[f"expected_{field}"] = expected
            pred_row[f"predicted_{field}"] = predicted
            pred_row[f"{field}_correct"] = correct

        predictions_rows.append(pred_row)

    total_elapsed_s = time.perf_counter() - start
    repo.clear_for_testing()

    predictions_df = pd.DataFrame(predictions_rows)
    predictions_path = TEST_DATA_DIR / "ocr_predictions.csv"
    predictions_df.to_csv(predictions_path, index=False)

    field_accuracy_rows = []
    total_correct = 0
    total_fields = 0
    for field in EVALUATED_FIELDS:
        correct = field_correct[field]
        total = field_total[field]
        accuracy = round((correct / total) * 100, 2) if total else 0.0
        field_accuracy_rows.append({
            "field": field, "total_tested": total, "correct": correct, "accuracy_percent": accuracy,
        })
        total_correct += correct
        total_fields += total

    overall_accuracy = round((total_correct / total_fields) * 100, 2) if total_fields else 0.0

    results_df = pd.DataFrame(field_accuracy_rows)
    results_path = TEST_DATA_DIR / "ocr_evaluation_results.csv"
    results_df.to_csv(results_path, index=False)

    summary = {
        "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "dataset_size": len(df),
        "evaluated_fields": EVALUATED_FIELDS,
        "field_accuracy": {r["field"]: r["accuracy_percent"] for r in field_accuracy_rows},
        "overall_field_level_accuracy_percent": overall_accuracy,
        "project_target_percent": 95,
        "target_achieved": overall_accuracy >= 95.0,
        "ocr_status_counts": ocr_status_counts,
        "extraction_status_counts": extraction_status_counts,
        "performance_ms": {
            "ocr_mean": round(sum(ocr_processing_times) / len(ocr_processing_times), 2) if ocr_processing_times else None,
            "ocr_max": round(max(ocr_processing_times), 2) if ocr_processing_times else None,
            "extraction_mean": round(sum(extraction_processing_times) / len(extraction_processing_times), 2) if extraction_processing_times else None,
            "extraction_max": round(max(extraction_processing_times), 2) if extraction_processing_times else None,
        },
        "total_evaluation_wall_time_seconds": round(total_elapsed_s, 2),
        "note": (
            "Ground truth is the value actually printed on each cheque image, "
            "not the bank's expected_* record -- OCR can only read what is "
            "physically on the page. This is a measured result from running "
            "the real pipeline against the Milestone 1 synthetic dataset; it "
            "is not a claim about production or real-world OCR accuracy."
        ),
    }
    summary_path = TEST_DATA_DIR / "ocr_evaluation_summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, default=str)

    return summary


if __name__ == "__main__":
    summary = run_evaluation()
    print(json.dumps(summary, indent=2))
