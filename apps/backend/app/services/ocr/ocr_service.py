"""OCR orchestration (docs/14_OCR_Engine.md S6, S16-S17).

Runs the configured OCREngine against Milestone 2's processed image. If
the result comes back LOW_CONFIDENCE, retries once against the original
(unprocessed) image as an alternate representation -- a concrete, simple
version of the documented "Attempt 1 standard preprocessing -> OCR ->
low confidence -> Attempt 2 enhanced preprocessing -> OCR -> compare
results" strategy (docs/14 S17), bounded to a single retry so it cannot
threaten the <30s/cheque budget.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

from app.services.ocr.engine import OCREngine, OCRRawResult
from app.services.ocr.exceptions import OCREngineUnavailableError
from app.services.ocr.tesseract_engine import get_ocr_engine
from app.services.preprocessing.preprocessing_service import load_image_bgr


@dataclass
class OCRRunOutcome:
    result: OCRRawResult
    attempts: int
    total_processing_time_ms: float


def run_ocr_for_cheque(
    processed_image_path: str,
    original_image_path: str,
    *,
    engine: OCREngine | None = None,
) -> OCRRunOutcome:
    engine = engine or get_ocr_engine()
    start = time.perf_counter()
    attempts = 0

    try:
        processed_image = load_image_bgr(processed_image_path)
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = (time.perf_counter() - start) * 1000
        failed = OCRRawResult(
            engine_name=engine.name, engine_version=engine.version, raw_text="",
            status="FAILED", error_message=f"Unable to load processed image: {exc}",
            processing_time_ms=elapsed_ms,
        )
        return OCRRunOutcome(result=failed, attempts=0, total_processing_time_ms=elapsed_ms)

    try:
        result = engine.run(processed_image)
        attempts += 1
    except OCREngineUnavailableError as exc:
        elapsed_ms = (time.perf_counter() - start) * 1000
        failed = OCRRawResult(
            engine_name=engine.name, engine_version="unavailable", raw_text="",
            status="FAILED", error_message=str(exc), processing_time_ms=elapsed_ms,
        )
        return OCRRunOutcome(result=failed, attempts=attempts, total_processing_time_ms=elapsed_ms)

    if result.status == "LOW_CONFIDENCE":
        try:
            original_image = load_image_bgr(original_image_path)
            retry_result = engine.run(original_image)
            attempts += 1
            if retry_result.average_confidence > result.average_confidence:
                result = retry_result
        except Exception:  # noqa: BLE001 - retry is best-effort; keep the first result on any failure
            pass

    total_elapsed_ms = (time.perf_counter() - start) * 1000
    return OCRRunOutcome(result=result, attempts=attempts, total_processing_time_ms=total_elapsed_ms)
