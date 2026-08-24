"""Cheque input orchestration (docs/12_Cheque_Input_Module.md S22).

Ties together file validation, storage, Processing ID generation, and a
handoff into the preprocessing pipeline -- exactly the responsibilities
documented for this module (docs/12 S27), and no further: this service
does not run OCR, extraction, validation, or fraud analysis.
"""

from __future__ import annotations

from datetime import datetime, timezone

from app.repositories.cheque_repository import get_cheque_repository
from app.services.audit import audit_service
from app.services.cheque import file_validation, id_generator, pdf_conversion, storage
from app.services.cheque.exceptions import ChequeInputError
from app.services.preprocessing.preprocessing_service import load_image_bgr, preprocess_image

import io


def handle_upload(filename: str | None, content: bytes, *, input_source: str = "UPLOAD") -> dict:
    """Runs file validation, then (if valid) registers the cheque and runs
    preprocessing synchronously. Raises ChequeInputError subclasses for
    anything that should be rejected before a Processing ID is ever
    issued (docs/12 S16: the REJECTED response has no cheque_id)."""

    validated = file_validation.validate_upload(filename, content)

    cheque_id = id_generator.generate_processing_id()
    file_hash = storage.sha256_hex(content)
    upload_timestamp = datetime.now(timezone.utc).isoformat()

    storage.save_original(cheque_id, validated.extension, content)

    record: dict = {
        "cheque_id": cheque_id,
        "file_name": validated.safe_filename,
        "file_type": validated.media_type,
        "file_size": validated.file_size,
        "input_source": input_source,
        "upload_timestamp": upload_timestamp,
        "file_hash": file_hash,
        "original_width": validated.width,
        "original_height": validated.height,
        "pdf_page_count": None,
        "processing_status": "UPLOADED",
        "preprocessing": None,
        "error": None,
    }
    repo = get_cheque_repository()
    repo.save(cheque_id, record)
    audit_service.record(
        event_type="CHEQUE_UPLOADED", cheque_id=cheque_id, source="USER",
        new_status="UPLOADED", action="UPLOAD", result="SUCCESS",
    )

    try:
        if validated.is_pdf:
            image, page_count = pdf_conversion.render_first_page_to_image(content)
            repo.update(cheque_id, {"pdf_page_count": page_count})
            height, width = image.shape[:2]
            repo.update(cheque_id, {"original_width": int(width), "original_height": int(height)})
        else:
            image = load_image_bgr(io.BytesIO(content))

        repo.update(cheque_id, {"processing_status": "PROCESSING"})
        result = preprocess_image(cheque_id, image)
        new_status = "PROCESSING" if result.preprocessing_status == "COMPLETED" else "FAILED"
        repo.update(cheque_id, {"preprocessing": result.as_dict(), "processing_status": new_status})
    except Exception:  # noqa: BLE001 - never let a preprocessing failure crash the upload request
        repo.update(cheque_id, {
            "processing_status": "FAILED",
            "error": {"code": "PREPROCESSING_ERROR", "message": "Cheque could not be processed. Please retry."},
        })

    return repo.get(cheque_id)  # type: ignore[return-value]


def get_cheque_record(cheque_id: str) -> dict | None:
    return get_cheque_repository().get(cheque_id)
